#!/bin/sh
sudo patch /opt/bitnami/guacamole/webroot/index.html index.html.patch
sudo patch /opt/bitnami/guacamole/webroot/index.html index2.html.patch
sudo /opt/bitnami/nami/bin/nami restart apache
