# Examples

## Running the examples

Once you have installed flask-ldap-login, 

## Check the configuration

    flask-ldap-login-check direct_bind:app -u testusername -p test password

This should return the userdata for your test user *testusername*

## Launch the app

    python direct_bind.py

Then open your browser and navigate to the login page: `/ldap/login`
