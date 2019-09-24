#!/usr/bin/env bash
#
# test_cronjob.sh
#
# test automation

TEST_HOME=/Users/christopherroeder/work/git/test

# PREREQUISITES:
# assume test/back_end  will be wiped and re-cloned
# assume python is installed, packages pipped
# assume postgresql is installed, environment variables set
# assume PGUSER == `whoami`
# assume PGUSER has a database with that name. Not used, but Postgresql insists on it as a default.
# PGHOST (localhost for now)
# PGPORT (5432 for now)
# PGDATABASE (created)
# PGUSER (whoami)
# PGPASSWORD (not used)


# TOOD bin/build.sh assumes locations for studies and OHDSI base db
#OHDSI_BASE=/Users/christopherroeder/backups/posterity/ohdsi_20170907.no_owner.gz
#STUDIES=/Users/christopherroeder/work/local/studies

# fail on errors
set -e 
set -o pipefail

cd $TEST_HOME
rm -rf  $TEST_HOME/back_end
pwd
git clone git@bitbucket.org:hfclinicaldata/back_end.git
cd back_end
mkdir test_logs

NAME="heart_test_$(date +%Y%m%d)"
echo "drop database $NAME" | psql

##bin/build.sh PIP3    TEST   &> test_logs/pip3.log

bin/build.sh OHDSI     TEST &> test_logs/ohdsi.log  # load base OHDSI
bin/build.sh BUILD     TEST &> test_logs/build.log  # load studies
bin/build.sh META      TEST &> test_logs/meta.log   # load mapping config
bin/build.sh MIGRATE   TEST &> test_logs/migrate.log
bin/build.sh CALCULATE TEST &> test_logs/calculate.log
bin/build.sh EXTRACT   TEST &> test_logs/extract.log

bin/build.sh CHECK    TEST &> test_logs/check.log
bin/build.sh REPORT   TEST &> test_logs/report.log
bin/build.sh ANALYZE  TEST &> test_logs/analyze.log
bin/build.sh UTEST    TEST &> test_logs/utest.log
bin/build.sh TEST     TEST &> test_logs/test.log

