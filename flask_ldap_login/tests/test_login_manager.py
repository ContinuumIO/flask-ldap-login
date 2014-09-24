import unittest

import flask
from flask_testing import TestCase as FlaskTestCase

from flask_ldap_login import LDAPLoginManager

from flask_ldap_login.tests.fixture import LDAPTestFixture


class TestLoginManager(LDAPTestFixture, FlaskTestCase):

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
