"""
Check that application ldap creds are set up correctly.
"""
from argparse import ArgumentParser
from pprint import pprint

from werkzeug.utils import import_string


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('app_module',
                        metavar='APP_MODULE',
                        help='Python importible flask application e.g. my.module:app')
    parser.add_argument('-u', '--username', required=True,
                        help='Ldap login with this username')
    parser.add_argument('-p', '--password', required=True,
                        help='Ldap login with this password')
    args = parser.parse_args()

    if ':' in args.app_module:
        import_name, appname = args.app_module.split(':', 1)
    else:
        import_name, appname = args.app_module, 'app'

    module = import_string(import_name)
    app = getattr(module, appname)

    userdata = app.ldap_login_manager.ldap_login(args.username, args.password)
    if userdata is None:
        print "Invalid username/password"
    else:
        print "Got userdata for %s" % args.username
        pprint(userdata)


if __name__ == '__main__':
    main()
