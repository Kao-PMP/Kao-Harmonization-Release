#!/usr/bin/env bash
#
# build_docker.sh
#
# a script to build docker images, local docker tarfiles of them, and build a deployment tarball from
# them an other stuff waiting in ~/ubuntu_share/test.
# Two different db images are created, db and db-outside, with container-local and outside storage,
# respectively. Only one is (should be) used at a time. See the two docker-compose files.
#
# creates ~/ubuntu_share/test.tgz
#

# from top-level django_harmonization (git, not django project) directory

rm harmonization_ui.tar
rm harmonization_ui.tar.gz
rm ~/ubuntu_share/test/harmonization_ui.tar.gz
rm ~/ubuntu_share/test/db.tar.gz
rm ~/ubuntu_share/test/env.list
rm ~/ubuntu_share/test/docker-compose.yml

ls ~/ubuntu_share/test

set -e

# -- harmonization_ui --
# Django
docker build -f Dockerfile.dev -t harmonization_ui .
docker save harmonization_ui > harmonization_ui.tar
gzip -f harmonization_ui.tar

# -- harmonization_ui RDS --
# Django
docker build -f Dockerfile.rds -t harmonization_ui_rds .
docker save harmonization_ui_rds > harmonization_ui_rds.tar
gzip -f harmonization_ui_rds.tar

# -- db-outside --
# postgresql with in-container storage
docker build -f Dockerfile.postgresql -t db .
docker save db > db.tar
gzip -f db.tar

## -- db --
# postgresql with outside storage
docker build -f Dockerfile.postgresql.outside -t db-outside .
docker save db-outside > db-outside.tar
gzip -f db-outside.tar

cp env.list ~/ubuntu_share/test
cp docker-compose.yml ~/ubuntu_share/test
cp bin/run_new_docker.sh ~/ubuntu_share/test

# stand-alone, use RDS
cp harmonization_ui_rds.tar.gz ~/ubuntu_share/test

# with one of the two db images 
#cp harmonization_ui.tar.gz ~/ubuntu_share/test
#cp db-outside.tar.gz ~/ubuntu_share/test
#cp db.tar.gz ~/ubuntu_share/test

cd ~/ubuntu_share
tar czf test.tgz test


