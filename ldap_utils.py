import os, json
import ldap
import subprocess

"""
Open and load a file at the json format
"""

CONFIG_FILE = 'config.json'

def open_and_load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as config_file:
            return json.loads(config_file.read())
    else:
        print("File [%s] doesn't exist, aborting." % (CONFIG_FILE))
        sys.exit(1)

def kinit(config):
    subprocess.check_call("/usr/bin/kinit -kt %s %s" % (config["krb5_keytab"], config["krb5_principal"]), shell=True)


def connect_ldap(config):
    try:
        kinit(config)
        con = ldap.initialize('ldaps://%s' % config["ldap_host"])
        auth_tokens = ldap.sasl.gssapi()
        con.sasl_interactive_bind_s('', auth_tokens)
    except Exception as e:
        return {'error': str(e)}, 422
    return con
  
def get_ldap_users(config, con, uid):
    logins = []
    results = con.search_s(config["ldap_base"], ldap.SCOPE_SUBTREE, "(uid=%s)" % uid,  ['uid'])
    for dn,entry in results:
        login = entry['uid'][0].decode('utf8')
        logins.append(login)
    print("%d ldap users" % len(logins))
    return logins
