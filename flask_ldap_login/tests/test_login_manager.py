import unittest
from flask_ldap_login import LDAPLoginManager
from flask_testing import TestCase as FlaskTestCase
import flask
from mock import patch
import ldap

#===============================================================================
# Create Mock LDAP user config
#===============================================================================

MOCK_LDAP_USERS = {('x=user1', 'pass1'): [['x=user1', {'key':['value1'],
                                                   'uid':'user1'}]],
              ('x=user2', 'pass2'):[['x=user2', {'key':['value2'],
                                             'uid':'user2'}]]}

def simple_bind_s(username, password):
    if (username, password) not in MOCK_LDAP_USERS:
        raise ldap.INVALID_CREDENTIALS
    return True

def test_keys(keys, results):

    results = results[1]
    for k, v in keys:
        if k not in results:
            return False
        if results[k] == v or results[k] == [v]:
            return True

def search_s(base, scope, filtstr=None, attrlist=None):
    if filtstr:
        keys = [filt.split('=', 1) for filt in filtstr.split(',')]
        for (user, _), results in MOCK_LDAP_USERS.items():
            for result in results:
                if test_keys(keys, result):
                    return results
    else:
        for (user, _), results in MOCK_LDAP_USERS.items():
            if base == user:
                return results
#===============================================================================
#
#===============================================================================
class TestLoginManager(FlaskTestCase):

    def setUp(self):
        FlaskTestCase.setUp(self)

        self._init_patch = patch('ldap.initialize')
        self._ldap_init = self._init_patch.start()
        self._ldap_init().simple_bind_s = simple_bind_s
        self._ldap_init().search_s = search_s

    def tearDown(self):
        FlaskTestCase.tearDown(self)
        self._init_patch.stop()


    def create_app(self):
        return flask.Flask(__name__)


    def test_direct_bind(self):
        LDAP = dict(BIND_DN='x=%(username)s')
        self.app.config.update(LDAP=LDAP)
        loginmanager = LDAPLoginManager(self.app)
        loginmanager.connect()

        result = loginmanager.direct_bind('username', 'password')
        self.assertIsNone(result)

        result = loginmanager.direct_bind('user1', 'pass1')
        self.assertIsNotNone(result)
        self.assertEqual(result, {'key': 'value1', 'uid': 'user1'})

    def test_direct_bind_keymap(self):

        LDAP = dict(BIND_DN='x=%(username)s', KEY_MAP={'transformed_key':'key'})
        self.app.config.update(LDAP=LDAP)

        loginmanager = LDAPLoginManager(self.app)
        loginmanager.connect()

        result = loginmanager.direct_bind('user1', 'pass1')
        self.assertIsNotNone(result)
        self.assertEqual(result, {'transformed_key': 'value1'})

    def test_bind_search(self):
        """
        This test will fail with out the pull request
        https://github.com/ContinuumIO/flask-ldap-login/pull/6 
        """
        LDAP = dict(BIND_DN='x=user1', BIND_AUTH='pass1',
                    USER_SEARCH=[{'base':'base', 'filter':'uid=%(username)s'}])
        self.app.config.update(LDAP=LDAP)

        loginmanager = LDAPLoginManager(self.app)
        loginmanager.connect()

        result = loginmanager.bind_search('user1', 'pass2')
        self.assertIsNone(result)

        result = loginmanager.bind_search('user1', 'pass1')
        self.assertIsNotNone(result)
        self.assertEqual(result, {'key': 'value1', 'uid': 'user1'})

    def test_bind_search_keymap(self):

        LDAP = dict(BIND_DN='x=user1', BIND_AUTH='pass1',
                    USER_SEARCH=[{'base':'base', 'filter':'uid=%(username)s'}],
                    KEY_MAP={'transformed_key':'key'})
        self.app.config.update(LDAP=LDAP)

        loginmanager = LDAPLoginManager(self.app)
        loginmanager.connect()

        result = loginmanager.bind_search('user1', 'pass1')
        self.assertIsNotNone(result)
        self.assertEqual(result, {'transformed_key': 'value1'})




if __name__ == '__main__':
    unittest.main()
