#!/usr/bin/env python

import os, binascii, json, random, string
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

def get_random_alphanumeric_string(length):
    letters_and_digits = string.ascii_letters + string.digits
    result_str = ''.join((random.choice(letters_and_digits) for i in range(length)))
    return result_str

if __name__ == '__main__':
    import sys, os
    from subprocess import Popen, PIPE
    
#    print('this script does not work as expected, use vnc.pl')
    if (os.path.exists("vnc.pl")):
        if len(sys.argv) > 1:
            p = sys.argv[1]
            if (p == "random"):
                p = get_random_alphanumeric_string(8)
        else:
            config = open_and_load_config()
            p = config["guac_vnc_pass"]
            
        output = Popen(["./vnc.pl", p], stdout=PIPE).communicate()[0]
        print("guacamole_vnc_password: %s" % p)
        print("guacamole_vnc_encrypted_password: %s" % output)
