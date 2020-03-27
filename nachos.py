#!/usr/bin/env python

import os, json, sys

from guacamole import *
from ldap_utils import *


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

# check USERS to create and delete

    users_to_create = []
    for user in ldap_users:
        if user not in guacamole_users:
            users_to_create.append(user)
    print("%d users to create" % len(users_to_create))


    users_to_delete = []
    for user in guacamole_users:
        if (guacamole_users[user]['attributes']['guac-organization'] == config["guac_group"]):
            if (user) not in ldap_users:
                users_to_delete.append(user)
                print("REM %s", user)
    print("%d users to delete" % len(users_to_delete))

    
# create USERS (in LDAP but not in Guacamole yet)
    
    if False:
        for user in users_to_create:
            passwd = get_rand_pass()
            print("create_user:   %-8s : %s" % (user, passwd))
            create_user(config, auth, user, passwd)


# delete USERS (no more in LDAP)

        
    for user in users_to_delete:
        print("delete_user:   %-8s" % user)
        print(guac_del_user(config, auth, user))

   
# optionnal: set random pass on existing users

    if False:
        print("set random pass")
        for user in guacamole_users:
            if (guacamole_users[user]['attributes']['guac-organization'] == config["guac_group"]):
                if (user) in ldap_users:
                    passwd = get_rand_pass()
                    print("update_user_pass   %-8s : %s" % (user, passwd))
                    update_user_pass(config, auth, user, passwd)

# scan network

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

