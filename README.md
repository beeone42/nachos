# nachos
to make guacamole better


1. Setup:

```
sudo apt-get install libsasl2-dev python-dev libldap2-dev libssl-dev
sudo apt-get install libsasl2-modules-gssapi-mit ldap-utils
sudo apt-get install krb5-user

sudo apt install python3-pip
pip3 install requests
pip3 install python-ldap

cp config.sample.json config.json
emacs config.json

python3 nachos.py

```

2. Profit !


To create your keytab:

```
[kdc1][root][~]# kadmin.local
kadmin.local:  add_principal -randkey nachos/guacamole@42CAMPUS.ORG
Principal "nachos/guacamole@42CAMPUS.ORG" created.
kadmin.local:  ktadd -k nachos.keytab nachos/guacamole@42CAMPUS.ORG
kadmin.local:  quit
[kdc1][root][~]#
```
