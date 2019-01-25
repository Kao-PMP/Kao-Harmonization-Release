#!/usr/bin/env bash

# run_postgres
#
# A script to initialize a database and then run postgres. To be called from within a Docker image.
#

PGHOST=127.0.0.1

PG_MAIN=/var/lib/postgresql-storage/main
mkdir $PG_MAIN
chown -R postgres $PG_MAIN
chmod -R 700 $PG_MAIN
echo "ok if that fails. Then you already have a database. Not removing it."



# -D flag must be getting overridden by what is in the conf file, so change the conf file
CONFIG=/etc/postgresql/9.6/main/postgresql.conf
NEW_CONFIG=/tmp/postgresql.conf
cat $CONFIG | sed -e 's\/var/lib/postgresql/9.6/main\/var/lib/postgresql-storage/main\' > $NEW_CONFIG
diff $CONFIG $NEW_CONFIG 
cp $NEW_CONFIG $CONFIG

echo "--- init ---"
/usr/lib/postgresql/9.6/bin/initdb -D $PG_MAIN

echo "-- stop because it seemd to need it --"
/usr/lib/postgresql/9.6/bin/pg_ctl -D $PG_MAIN stop

echo "--- starting so we can create user"
export PGUSER=''
export PGDATABASE=''
/usr/lib/postgresql/9.6/bin/pg_ctl -D $PG_MAIN start
sleep 5

echo "-- creating docker user"
psql  --command "CREATE USER docker WITH SUPERUSER PASSWORD 'docker';"
echo "create user status: $?"

echo "-- creating db"
createdb -O docker docker

echo "-- stopping...so I can restart in a way that Docker will stay open/on/up"
/usr/lib/postgresql/9.6/bin/pg_ctl -D $PG_MAIN stop

echo "-- start for real --"
/usr/lib/postgresql/9.6/bin/postgres -D $PG_MAIN -c config_file=$CONFIG

# and the docker-compose.yml file will have /var/lib/postgresql mapped somewhere safe and durable.
# typically /var/lib/postgresql-storage/main
export PGUSER='docker'
