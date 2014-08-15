import ldap

def scalar(value):
    if isinstance(value, (list, tuple)) and len(value) == 1:
        return value[0]
    return value

def format_results(results, keymap=None):
    if not results:
        return None
    userobj = results[0][1]
    if keymap:
        return {key:scalar(userobj.get(value)) for key, value in keymap.items()}
    else:
        return {key:scalar(value) for key, value in userobj.items()}


class LDAPLoginManager(object):
    def __init__(self, app=None):

        if app is not None:
            self.init_app(app)

        if not isinstance(self.config['USER_SEARCH'], list):
            self.config['USER_SEARCH'] = [self.config['USER_SEARCH']]

        self._save_user = None


    def init_app(self, app):
        self._config = app.config.get('LDAP')
        app.ldap_login_manager = self

    def save_user(self, func):
        self._save_user = func
        return func

    @property
    def config(self):
        return self._config

    def ldap_login(self, username, password):

        ld = ldap.initialize(self.config['URI'])

        ctx = {'username':username, 'password':password}
        user = self.config['USER_DN'] % ctx

        bind_auth = self.config.get('BIND_AUTH', password)
        try:
            ld.simple_bind_s(user, bind_auth)
        except ldap.INVALID_CREDENTIALS:
            return None


        results = None
        for search in self.config['USER_SEARCH']:
            base = search['base']
            filt = search['filter'] % ctx
            scope = search.get('scope', ldap.SCOPE_SUBTREE)
            keymap = self.config.get('KEY_MAP')
            if keymap:
                attrlist = keymap.values()
            else:
                attrlist = None
            results = ld.search_s(base, scope, filt, attrlist=attrlist)
            if results:
                break

        ld.unbind_s()

        return format_results(results, keymap)

from flask import current_app, flash
from flask.ext import wtf

class LDAPLoginForm(wtf.Form):

    username = wtf.TextField('Username', validators=[wtf.Required()])
    password = wtf.TextField('Password', validators=[wtf.Required()])

    def validate(self, *args, **kwargs):

        valid = wtf.Form.validate(self, *args, **kwargs)
        if not valid: return valid

        ldap_mgr = current_app.ldap_login_manager
        username = self.username.data
        password = self.password.data
        try:
            userdata = ldap_mgr.ldap_login(username, password)
        except ldap.INVALID_CREDENTIALS:
            flash("Invalid LDAP credentials", 'danger')
            return False
        except ldap.LDAPError as err:
            if isinstance(err.message, dict):
                message = err.message.get('desc', str(err))
            else:
                message = str(err.message)
            flash(message, 'danger')
            return False

        if userdata is None:
            flash("Invalid LDAP credentials", 'danger')
            return False

        self.user = ldap_mgr._save_user(username, userdata)
        return True

