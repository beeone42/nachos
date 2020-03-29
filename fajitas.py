#!/usr/bin/env python

from bottle import route, run, get, post, request, template
import os, json, requests, urllib.parse

from guacamole import *
from ldap_utils import *

CONFIG_FILE = 'config.json'

def get_intra_infos(token):
    url = config["intra_infos_url"]
    params = [("access_token", token)]
    r = requests.request(
        method = "GET",
        url = url,
        params = params
    )
    if r.status_code != 200:
        print(r.content)
        return False
    try:
        return r.json()
    except json.JSONDecodeError:
        print('Could not decode JSON response')
    print(r.content)
    return False
        
def get_intra_token(code):
    url = config["intra_token_url"]
    params = [
        ("grant_type",    "authorization_code"),
        ("client_id",     config["intra_client_id"]),
        ("client_secret", config["intra_client_secret"]),
        ("code",          code),
        ("redirect_uri",  config["fajitas_url"])
    ]
#    print(params)
    r = requests.request(
        method = "POST",
        url = url,
        params = params
    )
    try:
        j = r.json()
        if "access_token" not in j:
            print('No access_token in json result')
        else:
            return j["access_token"]
    except json.JSONDecodeError:
        print('Could not decode JSON response')
    print(r.content)
    return False

def get_intra_oauth_url():
    url = ("%s?client_id=%s&redirect_uri=%s&response_type=code" %
           (config["intra_authorize_url"],
            config["intra_client_id"],
            urllib.parse.quote(config["fajitas_url"], safe=''))
    )
    return url
    
@route('/')
def hello():
    if 'Authorization' in request.headers:
        return (request.headers.get('Authorization'))
    else:
        return template('hello', url=get_intra_oauth_url())

@route('/register')
def register():
    code = request.query.get('code')
    token = get_intra_token(code)
    print(token)
    if token == False:
        return template('failed', url=get_intra_oauth_url())
    
    infos = get_intra_infos(token)
    login = infos['login']

    con = connect_ldap(config)
    linfo = get_ldap_users(config, con, login)
    if (len(linfo) == 0):
        return template('not-found', login = login)
    
    return template('register', url=get_intra_oauth_url(), token=token, infos=infos)

@route('/set', method='POST')
def set_passwd():
    token = request.forms.get('token')
    password = request.forms.get('password')
    infos = get_intra_infos(token)
    login = infos['login']

    con = connect_ldap(config)
    linfo = get_ldap_users(config, con, login)
    if (len(linfo) == 0):
        return "%s does not exists on this Campus !" % login
    
    auth = guac_auth(config)
    try:
        user = guac_get_user(config, auth, login)
        print(user)
    except:
        create_user(config, auth, login, password)
        return "Success ! user created"
    
    update_user_pass(config, auth, login, password)
    return "Success ! password changed"
    

def get_guacamole_connections_all(config, auth):
    cs = guac_get_connections(config, auth, 'ROOT')
    res = {'groups':{}, 'con':{}}
    for grp in cs["childConnectionGroups"]:
        res['groups'][grp['name']] = {'active':grp['activeConnections']}
        if ("childConnections" in grp):
            for c in grp["childConnections"]:
                res['con'][c['identifier']] = {'name':c['name'],
                                       'proto':c['protocol']
                                       
                }
    return res

@route('/stats', method='GET')
def get_stats():
    auth = guac_auth(config)
    stats = guac_get_stats(config, auth)
    cons = get_guacamole_connections_all(config, auth)
    res = {}
    for s in stats:
        res[s] = {
            'login':stats[s]['username'],
            'ip':stats[s]['remoteHost'],
            'con':cons['con'][stats[s]['connectionIdentifier']]['name'],
            'proto':cons['con'][stats[s]['connectionIdentifier']]['proto'],
        }
    return res

if __name__ == "__main__":
    config = open_and_load_config()
    run(host=config["fajitas_host"], port=config["fajitas_port"], debug=config["debug"])
