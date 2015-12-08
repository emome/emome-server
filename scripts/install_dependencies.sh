#!/bin/bash
cd /var/www/emome-server
virtualenv venv
. venv/bin/activate
pip install -r requirements.txt
chown -R www-data:www-data /var/www/emome-server
