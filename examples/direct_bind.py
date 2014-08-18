from flask_ldap_login import LDAPLoginForm, LDAPLoginManager
from flask_login import login_user
from flask import request, render_template, redirect

#===============================================================================
# Config Vars
#===============================================================================
LDAP = {
    'URI': 'ldap://localhost:8389',

    # Bind directly to this base DN.
    'BIND_DN': 'uid=%(username)s,ou=People,dc=continuum,dc=io',

    # Map ldap keys into application specific keys
    'KEY_MAP': {
        'name':'cn',
        'company': 'o',
        'location':'l',
        'email': 'mail',
        },

    # LDAP connection options
    'OPTIONS': {
                'OPT_PROTOCOL_VERSION': 3,
                }
}

from base_app import app, User
app.config.update(LDAP=LDAP)
ldap_mgr = LDAPLoginManager(app)

# Store users in memory
users = {}

@ldap_mgr.save_user
def save_user(username, userdata):
    users[username] = User(username, userdata)
    return users[username]

@app.route('/ldap/login', methods=['GET', 'POST'])
def ldap_login():

    form = LDAPLoginForm(request.form)
    if form.validate_on_submit():
        login_user(form.user, remember=True)
        print "Valid"
        return redirect('/')
    else:
        print "Invalid"
    return render_template('login.html', form=form)

if __name__ == '__main__':

    username = 'hshi'
    password = 'ldaptest'

    app.run(host='0.0.0.0', port=4455, debug=True)
