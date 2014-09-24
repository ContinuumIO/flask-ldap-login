import unittest

import flask
from flask_testing import TestCase as FlaskTestCase

from flask_ldap_login import LDAPLoginManager

from flask_ldap_login.tests.fixture import LDAPTestFixture
from flask_ldap_login.forms import LDAPLoginForm, Form


class TestLoginForm(LDAPTestFixture, FlaskTestCase):

    def create_app(self):
        app = flask.Flask(__name__)
        LDAP = dict(BIND_DN='x=%(username)s')
        app.config.update(LDAP=LDAP)
        app.config['SECRET_KEY'] = 'abc123'

        mgr = LDAPLoginManager(app)
        mgr.save_user(self.save_user)
        return app

    def save_user(self, username, userdata):
        self._user = username, userdata

    def test_empty_login_form(self):

        Form
        with self.app.test_request_context('/login', method="POST", data={}):

            form = LDAPLoginForm(flask.request.form, csrf_enabled=False)
            self.assertFalse(form.validate_on_submit())
            self.assertIn('username', form.errors)
            self.assertIn('password', form.errors)

    def test_login_form(self):

        data = {'username':'user1', 'password':'pass1'}
        self._user = None
        with self.app.test_request_context('/login', method="POST", data=data):

            form = LDAPLoginForm(flask.request.form, csrf_enabled=False)
            self.assertTrue(form.validate_on_submit())

        # Test that save_user was called
        self.assertIsNotNone(self._user)


if __name__ == '__main__':
    unittest.main()
