import requests

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
            except JSONDecodeError:
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

