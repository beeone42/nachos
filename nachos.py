#!/usr/bin/env python

import os, json, sys
import ldap
import subprocess

from guacamole import *

CONFIG_FILE = 'config.json'

"""
Open and load a file at the json format
"""

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

def get_guacamole_users(config, auth):
    guacamole_users = guac_get_users(config, auth)
    print("%d guacamole users" % len(guacamole_users))
    return guacamole_users


def create_user(config, auth, user):
    group = config["guac_group"]
    payload = {"username":user,
               "password":"",
               "attributes":{
                   "guac-organization":group
               }}
    try:
        guac_add_user(config, auth, payload)
    except:
        print("failed guac_add_user")
    try:
        guac_add_user_to_group(config, auth, user, group)
    except Exception as e:
        print("failed guac_add_user_to_group")
        print(e)

"""
Main
"""

if __name__ == "__main__":
    config          = open_and_load_config()
    con             = connect_ldap(config)
    auth            = guac_auth(config)

    ldap_users      = get_ldap_users(config, con, "*")
    guacamole_users = get_guacamole_users(config, auth)

    users_to_delete = []
    for user in guacamole_users:
        if (guacamole_users[user]['attributes']['guac-organization'] == config["guac_group"]):
            if (user) not in ldap_users:
                users_to_delete.append(user)
                print("REM %s", user)
    print("%d users to delete" % len(users_to_delete))
            
    users_to_create = []
    for user in ldap_users:
        if user not in guacamole_users:
            users_to_create.append(user)
    print("%d users to create" % len(users_to_create))

    for user in users_to_create:
        print("create_user(%s)" % user)
        create_user(config, auth, user)

    
