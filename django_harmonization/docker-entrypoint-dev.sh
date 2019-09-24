#!/usr/bin/env bash

# docker-entrypoint-dev.sh
#
# docker-entry point for the Django image
# This one, intended for development, starts a SimpleHTTPServer so you can
# log in and bounce Django without the container shutting down. The SimpleHTTServer 
# isn't used for anything other than keeping the container up.

rm django.log

# duplicated from env.list which seems to have issues..
export PGHOST=db
export PGUSER=docker
export PGPORT=5432
export PGDATABASE=heart_db
export PGPASSWORD=docker

export PGDATABASE=docker
export PGDATABASE=heart_db

echo "serving host:$PGHOST port:$PGPORT user:$PGUSER pass:$PGPASSWORD db:$PGDATABASE" 
####echo "drop database heart_db;" | psql
####createdb heart_db
####python manage.py migrate 

echo "creating super user" 
echo "from django.contrib.auth.models import User; User.objects.filter(email='admin@example.com').delete(); User.objects.create_superuser('admin', 'admin@example.com', 'h8arm0n1z3')" | python manage.py shell 

# simple server just to hold the image up so you can log into a shell and exec django by hand repeatedly for debugging...
echo "running simple server on  port 8010, log in to run django and debug" 
/usr/bin/python -m SimpleHTTPServer 8010


