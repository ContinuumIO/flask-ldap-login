import ldap
from mock import patch
#===============================================================================
# Create Mock LDAP user config
#===============================================================================

MOCK_LDAP_USERS = {('x=user1', 'pass1'): [['x=user1', {'key':['value1'],
                                                   'uid':'user1'}]],
              ('x=user2', 'pass2'):[['x=user2', {'key':['value2'],
                                             'uid':'user2'}]]}

def simple_bind_s(username, password):
    if (username, password) not in MOCK_LDAP_USERS:
        raise ldap.INVALID_CREDENTIALS
    return True

def test_keys(keys, results):

    results = results[1]
    for k, v in keys:
        if k not in results:
            return False
        if results[k] == v or results[k] == [v]:
            return True

def search_s(base, scope, filtstr=None, attrlist=None):
    if filtstr:
        keys = [filt.split('=', 1) for filt in filtstr.split(',')]
        for (user, _), results in MOCK_LDAP_USERS.items():
            for result in results:
                if test_keys(keys, result):
                    return results
    else:
        for (user, _), results in MOCK_LDAP_USERS.items():
            if base == user:
                return results
#===============================================================================
#
#===============================================================================


class LDAPTestFixture(object):

    def setUp(self):

        self._init_patch = patch('ldap.initialize')
        self._ldap_init = self._init_patch.start()
        self._ldap_init().simple_bind_s = simple_bind_s
        self._ldap_init().search_s = search_s

    def tearDown(self):
        self._init_patch.stop()
