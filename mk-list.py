#!/usr/bin/env python

import os, json, sys

from guacamole import *
from ldap_utils import *


def check_host(ip):
    child = subprocess.Popen(["ping", "-c", "1", "-W", "1", ip], stdout = subprocess.PIPE)
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
    auth            = guac_auth(config)

    guacamole_users = get_guacamole_users(config, auth)
    ssh = get_guacamole_connections(config, auth, config["guac_tree_ssh"], "ssh")

    print("%s users, %s ssh" % (len(guacamole_users), len(ssh)))
    
    for user in guacamole_users:
        permissions = guac_get_user_permissions(config, auth, user)
        print(permissions['connectionPermissions'])
        ip, co = ssh.popitem()
        print("%s : %s/%s" % (user, ip, co))
        if user != "guacadmin":
            if co not in permissions.keys():
                print("need to add co %s" % co)
                guac_add_connection_to_user(config, auth, user, co)
            for co_id in permissions['connectionPermissions']:
                if co_id != co:
                    print("need to del co %s" % co_id)
                    guac_del_connection_to_user(config, auth, user, co_id)

            
