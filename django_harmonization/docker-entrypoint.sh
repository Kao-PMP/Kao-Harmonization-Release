#!/usr/bin/env bash

# docker-entrypoint.sh
#
# docker-entry point for the Django image

rm django.log

# duplicated from env.list which seems to have issues..
export PGHOST=db
export PGUSER=docker
export PGPORT=5432
export PGDATABASE=heart_db
export PGPASSWORD=docker


echo "serving host:$PGHOST port:$PGPORT user:$PGUSER pass:$PGPASSWORD db:$PGDATABASE" 
####echo "drop database heart_db;" | psql
####createdb heart_db
####python manage.py migrate 

echo "creating super user" 
echo "from django.contrib.auth.models import User; User.objects.filter(email='admin@example.com').delete(); User.objects.create_superuser('admin', 'admin@example.com', 'h8arm0n1z3')" | python manage.py shell 

 

echo "running on port 8000" 
python manage.py runserver 0.0.0.0:8000


