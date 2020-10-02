#!/usr/bin/env python

import os, binascii, json
import d3des as d # for brevity - narrow column

CONFIG_FILE = 'config.json'

def open_and_load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as config_file:
            return json.loads(config_file.read())
    else:
        print("File [%s] doesn't exist, aborting." % (CONFIG_FILE))
        sys.exit(1)


def get_vnc_enc(password):
    if (len(password) > 8):
        return get_vnc_enc(password[:8]) + get_vnc_enc(password[8:])
    else:
        b = bytearray(password, 'utf-8') 
        passpadd = (b + b'\x00' * 8)[:8]
    strkey = ''.join([ chr(x) for x in d.vnckey ])
    ekey = d.deskey(strkey, False)
    ctext = d.desfunc(passpadd, ekey)
    return binascii.hexlify(ctext).decode('utf-8')


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        print(get_vnc_enc(sys.argv[1]))
    else:
#        print('usage: %s <password>' % sys.argv[0])
        config = open_and_load_config()
        p = get_vnc_enc(config["guac_vnc_pass"])
        print("")
        print("vnc.crypt('%s') = %s" % (config["guac_vnc_pass"], p))
        print("")
        print("Add this to your ansiblecluster/roles/remote/defaults/main.yml")
        print("")
        print("guacamole_vnc_password_crypted: %s" % p)
        print("")
