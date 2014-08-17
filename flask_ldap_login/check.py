"""
Check that application ldap creds are set up correctly
"""
from argparse import ArgumentParser
from pprint import pprint
from werkzeug.utils import import_string

def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('-a', '--app', required=True)
    parser.add_argument('-u', '--username', required=True)
    parser.add_argument('-p', '--password', required=True)
    args = parser.parse_args()

    if ':' in args.app:
        import_name, appname = args.app.split(':', 1)
    else:
        import_name, appname = args.app, 'app'
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
