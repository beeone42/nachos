import requests, uuid

def guac_request(token, method, url, payload = None,
                 url_params = None, json_response = True):
        params = [('token', token)]
        if url_params:
            params += url_params
        r = requests.request(
            method = method,
            url = url,
            params = params,
            json = payload,
            allow_redirects = True
        )
        if not r.ok:
            print(r.content)
        r.raise_for_status()
        if r.status_code == 204:
                return ""
        if json_response:
            try:
                return r.json()
            except json.JSONDecodeError:
                print('Could not decode JSON response')
                return r
        else:
            return r

def guac_auth(config):
    r = requests.post(
        url             = config["guac_api"] + '/tokens',
        data            = {'username': config["guac_user"],
                           'password': config["guac_pass"]},
        allow_redirects = True
    )
    r.raise_for_status()
    return r.json()

def guac_get_stats(config, auth):
    return guac_request(
        token = auth["authToken"],
        method = 'GET',
        url = '{}/session/data/{}/activeConnections'.format(
            config["guac_api"],
            auth["dataSource"]
        )
    )
        
def guac_get_users(config, auth):
    return guac_request(
        token = auth["authToken"],
        method = 'GET',
        url = '{}/session/data/{}/users'.format(
            config["guac_api"],
            auth["dataSource"]
        )
    )

def guac_get_connections(config, auth, root):
    return guac_request(
        token = auth["authToken"],
        method = 'GET',
        url = '{}/session/data/{}/connectionGroups/ROOT/tree'.format(
                config["guac_api"],
                auth["dataSource"]
        )
    )


def guac_add_user(config, auth, payload):
    return guac_request(
        token = auth["authToken"],
        method = 'POST',
        url = '{}/session/data/{}/users'.format(
            config["guac_api"],
            auth["dataSource"]
        ),
        payload = payload
    )

def guac_get_user(config, auth, user):
    return guac_request(
        token = auth["authToken"],
        method = 'GET',
        url = '{}/session/data/{}/users/{}'.format(
                config["guac_api"],
                auth["dataSource"],
                user
        ),
        payload = {}
    )

def guac_update_user(config, auth, user, payload):
    return guac_request(
        token = auth["authToken"],
        method = 'PUT',
        url = '{}/session/data/{}/users/{}'.format(
                config["guac_api"],
                auth["dataSource"],
                user
        ),
        payload = payload
    )

def guac_del_user(config, auth, user):
    return guac_request(
        token = auth["authToken"],
        method = 'DELETE',
        url = '{}/session/data/{}/users/{}'.format(
                config["guac_api"],
                auth["dataSource"],
                user
        ),
        payload = {}
    )

def update_user_pass(config, auth, user, passwd):
    guac_update_user(config, auth, user,
                     {
                         "username":user,
                         "attributes":{},
                         "password":passwd
                     }
    )


def guac_add_user_to_group(config, auth, user, group):
    payload = [{"op": "add", "path": "/", "value": group}]
    return guac_request(
        token = auth["authToken"],
        method = 'PATCH',
        url = '{}/session/data/{}/users/{}/userGroups'.format(
            config["guac_api"], auth["dataSource"], user),
        payload = payload,
        json_response = False
    )

def guac_add_connection(config, auth, payload):
    return guac_request(
        token = auth["authToken"],
        method = 'POST',
        url = '{}/session/data/{}/connections'.format(
            config["guac_api"],
            auth["dataSource"]
        ),
        payload = payload
    )

def guac_del_connection(config, auth, id):
    return guac_request(
        token = auth["authToken"],
        method = 'DELETE',
        url = '{}/session/data/{}/connections/{}'.format(
                config["guac_api"],
                auth["dataSource"],
                id
        ),
        payload = {}
    )


def get_rand_pass():
    # generate random passwd
    return uuid.uuid4().hex

def create_user(config, auth, user, passwd):
    group = config["guac_group"]
    payload = {"username":user,
               "password":passwd,
               "attributes":{
                   "guac-organization":group
               }}
    try:
        print("create_user %s : %s" % (user, passwd))
        guac_add_user(config, auth, payload)
    except:
        print("failed guac_add_user")
    try:
        guac_add_user_to_group(config, auth, user, group)
    except Exception as e:
        print("failed guac_add_user_to_group")
        print(e)


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
    cs = guac_get_connections(config, auth, 'ROOT')
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

