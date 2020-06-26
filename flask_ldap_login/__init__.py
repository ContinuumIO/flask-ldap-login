"""
Configuration Variables
-----------------------

To set the flask-ldap-login config variables

update the application like::

    app.config.update(LDAP={'URI': ..., })
 
:param URI: 
    Start by setting URI to point to your server. 
    The value of this setting can be anything that your LDAP library supports. 
    For instance, openldap may allow you to give a comma- or space-separated 
    list of URIs to try in sequence.
    
:param BIND_DN:
    The distinguished name to use when binding to the LDAP server (with BIND_AUTH). 
    Use the empty string (the default) for an anonymous bind. 

:param BIND_AUTH:
    The password to use with BIND_DN
    
:param USER_SEARCH:
    An  dict that will locate a user in the directory.
    The dict object may contain 'base' (required), 'filter' (required) and 'scope' (optional)
    base: The base DN to search
    filter:  Should contain the placeholder %(username)s for the username.
    scope:  
     
    e.g.::
        {'base': 'dc=continuum,dc=io', 'filter': 'uid=%(username)s'}
        
:param KEY_MAP:
    This is a dict mapping application context to ldap.
    An application may expect user data to be consistent and not all ldap
    setups use the same configuration::
     
        'application_key': 'ldap_key'   


"""
import logging

import flask
import ldap

from .forms import LDAPLoginForm

log = logging.getLogger(__name__)

def scalar(value):
    """
    Take return a value[0] if `value` is a list of length 1
    """
    if isinstance(value, (list, tuple)) and len(value) == 1:
        return value[0]
    return value


def _is_utf8(s):
    try:
        if isinstance(s, str):
            us = s.decode('utf-8')

        return True
    except UnicodeDecodeError:
        return False

class LDAPLoginManager(object):
    '''
    This object is used to hold the settings used for LDAP user lookup. Instances of
    `LDAPLoginManager` are *not* bound to specific apps, so you can create
    one in the main body of your code and then bind it to your
    app in a factory function.
    '''

    def __init__(self, app=None):

        if app is not None:
            self.init_app(app)

        self._raise_errors = False
        self.conn = None
        self._save_user = None

    def set_raise_errors(self, state=True):
        '''
        Set the _raise_errors flags to allow for the calling code to provide error handling.
        This is especially helpful for debugging from flask_ldap_login_check.
        '''
        self._raise_errors = state

    def init_app(self, app):
        '''
        Configures an application. This registers an `after_request` call, and
        attaches this `LoginManager` to it as `app.ldap_login_manager`.
        '''

        self._config = app.config.get('LDAP', {})
        app.ldap_login_manager = self

        self.config.setdefault('BIND_DN', '')
        self.config.setdefault('BIND_AUTH', '')
        self.config.setdefault('URI', 'ldap://127.0.0.1')
        self.config.setdefault('OPTIONS', {})
        # Referrals are disabled by default
        self.config['OPTIONS'].setdefault(ldap.OPT_REFERRALS, ldap.OPT_OFF)

        if self.config.get('USER_SEARCH') and not isinstance(self.config['USER_SEARCH'], list):
            self.config['USER_SEARCH'] = [self.config['USER_SEARCH']]

    def format_results(self, results):
        """
        Format the ldap results object into somthing that is reasonable
        """
        if not results:
            return None
        userdn = results[0][0]
        userobj = results[0][1]
        userobj['dn'] = userdn

        keymap = self.config.get('KEY_MAP')
        if keymap:
            return {key:scalar(userobj.get(value)) for key, value in keymap.items() if _is_utf8(scalar(userobj.get(value))) }
        else:
            return {key:scalar(value) for key, value in userobj.items() if _is_utf8(scalar(value)) }

    def save_user(self, callback):
        '''
        This sets the callback for staving a user that has been looked up from from ldap. 
        The function you set should take a username (unicode) and and userdata (dict).

        :param callback: The callback for retrieving a user object.
        '''

        self._save_user = callback
        return callback

    @property
    def config(self):
        'LDAP config vars'
        return self._config

    @property
    def attrlist(self):
        'Transform the KEY_MAP paramiter into an attrlist for ldap filters'
        keymap = self.config.get('KEY_MAP')
        if keymap:
            # https://github.com/ContinuumIO/flask-ldap-login/issues/11
            # https://continuumsupport.zendesk.com/agent/tickets/393
            return [s.encode('utf-8') for s in keymap.values()]
        else:
            return None


    def bind_search(self, username, password):
        """
        Bind to BIND_DN/BIND_AUTH then search for user to perform lookup.
        """

        log.debug("Performing bind/search")

        ctx = {'username':username, 'password':password}

        user = self.config['BIND_DN'] % ctx

        bind_auth = self.config['BIND_AUTH']
        try:
            log.debug("Binding with the BIND_DN %s" % user)
            self.conn.simple_bind_s(user, bind_auth)
        except ldap.INVALID_CREDENTIALS:
            msg = "Could not connect bind with the BIND_DN=%s" % user
            log.debug(msg)
            if self._raise_errors:
                raise ldap.INVALID_CREDENTIALS(msg)
            return None

        user_search = self.config.get('USER_SEARCH')

        results = None
        found_user = False
        for search in user_search:
            base = search['base']
            filt = search['filter'] % ctx
            scope = search.get('scope', ldap.SCOPE_SUBTREE)
            log.debug("Search for base=%s filter=%s" % (base, filt))
            results = self.conn.search_s(base, scope, filt, attrlist=self.attrlist)
            if results:
                found_user = True
                log.debug("User with DN=%s found" % results[0][0])
                try:
                    self.conn.simple_bind_s(results[0][0], password)
                except ldap.INVALID_CREDENTIALS:
                    self.conn.simple_bind_s(user, bind_auth)
                    log.debug("Username/password mismatch, continue search...")
                    results = None
                    continue
                else:
                    log.debug("Username/password OK")
                    break
        if not results and self._raise_errors:
            msg = "No users found matching search criteria: {}".format(user_search)
            if found_user:
                msg = "Username/password mismatch"
            raise ldap.INVALID_CREDENTIALS(msg)

        log.debug("Unbind")
        self.conn.unbind_s()

        return self.format_results(results)


    def direct_bind(self, username, password):
        """
        Bind to username/password directly
        """
        log.debug("Performing direct bind")

        ctx = {'username':username, 'password':password}
        scope = self.config.get('SCOPE', ldap.SCOPE_SUBTREE)
        user = self.config['BIND_DN'] % ctx

        try:
            log.debug("Binding with the BIND_DN %s" % user)
            self.conn.simple_bind_s(user, password)
        except ldap.INVALID_CREDENTIALS:
            if self._raise_errors:
                raise ldap.INVALID_CREDENTIALS("Unable to do a direct bind with BIND_DN %s" % user)
            return None
        results = self.conn.search_s(user, scope, attrlist=self.attrlist)
        self.conn.unbind_s()
        return self.format_results(results)


    def connect(self):
        'initialize ldap connection and set options'
        log.debug("Connecting to ldap server %s" % self.config['URI'])
        self.conn = ldap.initialize(self.config['URI'])

        # There are some settings that can't be changed at runtime without a context restart.
        # It's possible to refresh the context and apply the settings by setting OPT_X_TLS_NEWCTX
        # to 0, but this needs to be the last option set, and since the config dictionary is not
        # sorted, this is not necessarily true. Sort the list of options so that if OPT_X_TLS_NEWCTX
        # is present, it is applied last.
        options = self.config.get('OPTIONS', {}).items()
        options.sort(key=lambda x: x[0] == 'OPT_X_TLS_NEWCTX')

        for opt, value in options:
            if isinstance(opt, str):
                opt = getattr(ldap, opt)

            try:
                if isinstance(value, str):
                    value = getattr(ldap, value)
            except AttributeError:
                pass
            self.conn.set_option(opt, value)

        if self.config.get('START_TLS'):
            log.debug("Starting TLS")
            self.conn.start_tls_s()

    def ldap_login(self, username, password):
        """
        Authenticate a user using ldap. This will return a userdata dict
        if successfull.
        ldap_login will return None if the user does not exist or if the credentials are invalid
        """
        self.connect()

        if self.config.get('USER_SEARCH'):
            result = self.bind_search(username, password)
        else:
            result = self.direct_bind(username, password)
        return result
