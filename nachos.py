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

def get_guacamole_connection_group_id(config, auth, root):
    cs = guac_get_connections(config, auth, root)
    for grp in cs["childConnectionGroups"]:
        if (grp["name"] == root):
            return grp["identifier"]
    return "-1"

def get_guacamole_connections(config, auth, root, kind):
    cs = guac_get_connections(config, auth, root)
    res = {}
    for grp in cs["childConnectionGroups"]:
        if (grp["name"] == root):
            if ("childConnections" in grp):
                for c in grp["childConnections"]:
                    infos = c["name"].split(":")
                    if len(infos) == 2:
                        if (infos[0] == kind):
                            res[infos[1]] = c["identifier"]
                        else:
                            print("bogus co:", c["name"])
                            guac_del_connection(config, auth, c["identifier"])
                    else:
                        print("bogus co:", c["name"])
                        guac_del_connection(config, auth, c["identifier"])
    return res

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


def check_host(ip):
    child = subprocess.Popen(["ping", "-c", "1", "-w", "1", ip], stdout = subprocess.PIPE)
    datas = child.communicate()[0]
    rcode = child.returncode
    return rcode == 0
    
def check_subnet(a, b, c, d):
    ips = []
    for i in range(b[0], b[1] + 1):
        for j in range(c[0], c[1] + 1):
            for k in range(d[0], d[1] + 1):
                ip = "%d.%d.%d.%d" % (a, i, j, k)
                r = check_host(ip)
                print(ip, r)
                if r:
                    ips.append(ip)
    return ips


def create_ssh_connection(config, auth, ip, ssh_id):
    print("create ssh", ip)
    payload = {"parentIdentifier":ssh_id,
               "name":"ssh:%s" % ip,
               "protocol":"ssh",
               "parameters":{"port":config["guac_ssh_port"],
                             "hostname":ip},
               "attributes":{"max-connections":config["guac_ssh_max_co"],
                             "max-connections-per-user":config["guac_ssh_max_per_user"]}
    }
    try:
        guac_add_connection(config, auth, payload)
    except:
        print("failed guac_add_connection")

def create_vnc_connection(config, auth, ip, vnc_id):
    print("create vnc", ip)
    payload = {"parentIdentifier":vnc_id,
               "name":"vnc:%s" % ip,
               "protocol":"vnc",
               "parameters":{"port":config["guac_vnc_port"],
                             "hostname":ip,
                             "password":config["guac_vnc_pass"]},
               "attributes":{"max-connections":config["guac_vnc_max_co"],
                             "max-connections-per-user":config["guac_vnc_max_per_user"]}
    }
    try:
        guac_add_connection(config, auth, payload)
    except:
        print("failed guac_add_connection")


        
"""
Main
"""


        
if __name__ == "__main__":
    config          = open_and_load_config()
    con             = connect_ldap(config)
    auth            = guac_auth(config)

    ldap_users      = get_ldap_users(config, con, "*")
    guacamole_users = get_guacamole_users(config, auth)

#    ldap_users      = []
#    guacamole_users = []

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
        
    for user in users_to_delete:
        print("delete_user(%s)" % user)
        print(guac_del_user(config, auth, user))

    
    ips = check_subnet(
        config["host_ips"]["a"],
        config["host_ips"]["b"],
        config["host_ips"]["c"],
        config["host_ips"]["d"])


# create SSH

    ssh = get_guacamole_connections(config, auth, config["guac_tree_ssh"], "ssh")
    ssh_id = get_guacamole_connection_group_id(config, auth, config["guac_tree_ssh"])

    for ip in ips:
        if ip not in ssh:
            create_ssh_connection(config, auth, ip, ssh_id)

# delete SSH
        
    for ip in ssh:
        if ip not in ips:
            print("delete SSH %s (%s)" % (ip, ssh[ip]))
            guac_del_connection(config, auth, ssh[ip])
    
        
# create VNC

    vnc = get_guacamole_connections(config, auth, config["guac_tree_vnc"], "vnc")
    vnc_id = get_guacamole_connection_group_id(config, auth, config["guac_tree_vnc"])

    for ip in ips:
        if ip not in vnc:
            create_vnc_connection(config, auth, ip, vnc_id)

# delete VNC
        
    for ip in vnc:
        if ip not in ips:
            print("delete VNC %s (%s)" % (ip, vnc[ip]))
            guac_del_connection(config, auth, vnc[ip])

