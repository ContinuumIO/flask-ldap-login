flask-ldap
==========

Flask ldap login is designed to work on top of an existing application.

It will:

 * Connect to an ldap server
 * Lookup ldap users using a direct bind or bind/search method
 * Store the ldap user into your server's DB
 * Integrate ldap into an existing web application

It will not:

 *  Provide `login_required` or any other route decorators
 *  Store the active user’s ID in the session. Use an existing framework like
    [Flask-Login](https://flask-login.readthedocs.org/en/latest/) for this task.

# Examples

 *  [Bind/Search](https://github.com/srossross/flask-ldap-login/blob/master/examples/bind_search.py)
 *  [Direct Bind](https://github.com/srossross/flask-ldap-login/blob/master/examples/direct_bind.py)

# Configuring your Application

The most important part of an application that uses flask-ldap-Login is the `LDAPLoginManager` class.
You should create one for your application somewhere in your code, like this:

    ldap_mgr = LDAPLoginManager()

The login manager contains the code that lets your application and ldap work together
such as how to load a user from an ldap server,
and how to store the user into the application's database.

Once the actual application object has been created, you can configure it for login with:

    login_manager.init_app(app)

# Testing your Configuration

Run the `flask-ldap-login-check` command against your app
to test that it can successully connect to your ldap server.

    flask-ldap-login-check examples.direct_bind:app --username 'me' --password 'super secret'

# How it Works

## save_user callback

You will need to provide a `save_user` callback.
This callback is used store any users looked up in the ldap diectory into your database. For example:
Callback must return a `user` object or `None` if the user can not be created.

    @ldap_mgr.save_user
    def save_user(username, userdata):
        user = User.get(username=username)
        if user is None:
            user = create_user(username, userdata)
        else:
            user.update(userdata)
            user.save()

        return user

## LDAPLoginForm form

The `LDAPLoginForm` is provided to you for your convinience.
Once validated the form  will contain a valid `form.user`
object which you can use in your application.
In this example, the user object is logged in using the `login_user` from The
[Flask-Login](https://flask-login.readthedocs.org/en/latest/) module:

    @app.route('/login', methods=['GET', 'POST'])
    def ldap_login():

        form = LDAPLoginForm(request.form)

        if form.validate_on_submit():
            login_user(form.user, remember=True)
            print "Valid"
            return redirect('/')
        else:
            print "Invalid"
        return render_template('login.html', form=form)

## Configuration Variables

To set the flask-ldap-login config variables

update the application like:

    app.config.update(LDAP={'URI': ..., })

### URI:

Start by setting URI to point to your server.
The value of this setting can be anything that your LDAP library supports.
For instance, openldap may allow you to give a comma- or space-separated
list of URIs to try in sequence.

### BIND_DN:

The distinguished name to use when binding to the LDAP server (with `BIND_AUTH`).
Use the empty string (the default) for an anonymous bind.

### BIND_AUTH

The password to use with `BIND_DN`

### USER_SEARCH

An  dict that will locate a user in the directory.
The dict object may contain `base` (required), `filter` (required) and `scope` (optional)

 * base: The base DN to search
 * filter:  Should contain the placeholder `%(username)s` for the username.
 * scope: TODO: document

e.g.:

    {'base': 'dc=continuum,dc=io', 'filter': 'uid=%(username)s'}

### KEY_MAP:

This is a dict mapping application context to ldap.
An application may expect user data to be consistant and not all ldap
setups use the same configuration:

    'application_key': 'ldap_key'

For example:

    KEY_MAP={'name':'cn', 'company': 'o', 'email': 'mail'}

### START_TLS

If `True`, each connection to the LDAP server will call `start_tls_s()`
to enable TLS encryption over the standard LDAP port.
There are a number of configuration options that can be given to `OPTIONS` that affect the TLS connection.
For example, `OPT_X_TLS_REQUIRE_CERT` can be set to `OPT_X_TLS_NEVER` to disable certificate verification,
perhaps to allow self-signed certificates.


### OPTIONS

This stores ldap specific options eg:

    LDAP={ 'OPTIONS': { 'OPT_PROTOCOL_VERSION': 3,
                        'OPT_X_TLS_REQUIRE_CERT': 'OPT_X_TLS_NEVER'
                      }
         }

## TLS (secure LDAP)

To enable a secure TLS connection you must set `START_TLS` to True.
There are a number of configuration options that can be given to `OPTIONS` that affect the TLS connection.
For example, `OPT_X_TLS_REQUIRE_CERT` `OPT_X_TLS_NEVER` to disable certificate verification, perhaps to allow self-signed certificates.


    LDAP={ 'START_TLS': True,
           'OPTIONS': { 'OPT_PROTOCOL_VERSION': 3,
                        'OPT_X_TLS_DEMAND', True,
                        'OPT_X_TLS_REQUIRE_CERT': 'OPT_X_TLS_NEVER',
                        'OPT_X_TLS_CACERTFILE', '/path/to/certfile')

                      }
         }

