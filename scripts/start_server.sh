#!/bin/bash
uwsgi --ini /var/www/emome-server/emome_uwsgi.ini &
PID=$!
sleep 2
kill $PID
chown -R www-data:www-data /var/www/emome-server
restart uwsgi
