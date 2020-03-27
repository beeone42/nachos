#!/usr/bin/env python

from bottle import route, run, get, post, request
import os, json, requests, urllib.parse

CONFIG_FILE = 'config.json'

def open_and_load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as config_file:
            return json.loads(config_file.read())
    else:
        print("File [%s] doesn't exist, aborting." % (CONFIG_FILE))
        sys.exit(1)

def get_intra_infos(token):
    return "{'result':'ok'}"
        
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

    
@route('/')
def hello():
    if 'Authorization' in request.headers:
        return (request.headers.get('Authorization'))
    else:
        return("%s?client_id=%s&redirect_uri=%sregister&response_type=code" %
                (config["intra_authorize_url"],
                 config["intra_client_id"],
                 urllib.parse.quote(config["fajitas_url"], safe=''))
               )

@route('/register')
def register():
    code = request.query.get('code')
    token = get_intra_token(code)
    print(token)
    infos = get_intra_infos(token)
    print(infos)
    return infos


if __name__ == "__main__":
    config = open_and_load_config()
    run(host=config["fajitas_host"], port=config["fajitas_port"], debug=config["debug"])
