# Examples

 * direct_bind.py
 * bind_search.py
 

## Running the examples

Once you have installed flask-ldap-login, 

## Check the configuration

    flask-ldap-login-check direct_bind:app -u testusername -p test password

This should return the userdata for your test user *testusername*

If it does not, or raises an exception, you will have to edit the LDAP config variable in `direct_bind.py`

## Launch the app

    python direct_bind.py

Then open your browser and navigate to the login page: `/ldap/login`
