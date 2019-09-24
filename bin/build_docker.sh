#!/usr/bin/env bash
#
# build_docker.sh
#
# builds a docker file and copies it into ~/ubuntu_share for the next step
# creates ~/ubuntu_share/test.tgz that includes data and other files for use outside docker
#

# from top-level django_harmonization (git, not django project) directory

# build targets
rm harmonization_ui.tar
rm harmonization_ui.tar.gz
rm harmonization_ui_rds.tar.gz
mkdir ~/ubuntu_share/test 2> /dev/null
rm    ~/ubuntu_share/test/harmonization_ui.tar.gz
rm    ~/ubuntu_share/test/harmonization_ui_rds.tar.gz
rm    ~/ubuntu_share/test/env.list
rm    ~/ubuntu_share/test/docker-compose.yml
rm    ~/ubuntu_share/test/run_new_docker.sh 

# noise
rm django_harmonization/debug.log
rm django_harmonization/django_harmonization/django.log
rm django_harmonization/django_harmonization/HeartData.log

##rm -f ~/ubuntu_share/test/ohdsi_20170907.no_owner
##rm -r ~/ubuntu_share/test/ohdsi_vocab_v5


set -e

# bump version, tag git, push
date "+%Y-%m-%d_%H-%M" > VERSION
version=$(cat VERSION)
git commit -m "version $version" VERSION
git tag -a "$version" -m "version $version"
git push
git push --tags


# create Docker file for django_harmonization
docker build -f Dockerfile.rds -t harmonization_ui_rds .
docker save harmonization_ui_rds > harmonization_ui_rds.tar
gzip -f harmonization_ui_rds.tar


# if using a repo...
#docker tag $USERNAME/$IMAGE:latest $USERNAME/$IMAGE:$version

# build a tarfile of stuff to ship to deployment machine
cp harmonization_ui_rds.tar.gz ~/ubuntu_share/test
cp env.list ~/ubuntu_share/test
cp docker-compose.yml ~/ubuntu_share/test
cp bin/run_new_docker.sh ~/ubuntu_share/test

##cp ../ohdsi_20170907.no_owner ~/ubuntu_share/test
cp ../ohdsi_vocab_v5.tgz ~/ubuntu_share

cd ~/ubuntu_share
tar czf test_$version.tgz test


