from flask.ext.wtf import Form
import wtforms
from wtforms import validators
from flask import flash, current_app
import ldap

class LDAPLoginForm(Form):
    """
    This is a form to be subclassed by your application. 
    
    Once validiated will have a `form.user` object that contains 
    a user object.
    """

    username = wtforms.TextField('Username', validators=[validators.Required()])
    password = wtforms.PasswordField('Password', validators=[validators.Required()])
    remember_me = wtforms.BooleanField('Remember Me', default=True)

    def validate_ldap(self):
        'Validate the username/password data against ldap directory'
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


    def validate(self, *args, **kwargs):
        """
        Validates the form by calling `validate` on each field, passing any
        extra `Form.validate_<fieldname>` validators to the field validator.
        
        also calls `validate_ldap` 
        """

        valid = Form.validate(self, *args, **kwargs)
        if not valid: return valid

        return self.validate_ldap()
