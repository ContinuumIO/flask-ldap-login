from argparse import ArgumentParser
from werkzeug.utils import import_string
from pprint import pprint


def main():
    parser = ArgumentParser()
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
        print "Got userdata for %s" % args.username
        pprint(userdata)
    else
        print "Invalid username/password"


if __name__ == '__main__':
    main()
