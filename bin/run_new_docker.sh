#!/usr/bin/env bash

# run_new_docker.sh
#
# given a new test.tgz deployment tarball, this script pulls it apart as required
# and starts up the two docker images: postgres and django


# as root,  from test dir that contains image files etc
# /mnt/workspace/chris_sync/test
# /mnt/workspace/chris_sync/output
mkdir /mnt/workspace/test
mkdir /mnt/workspace/output
mkdir /mnt/workspace/postgresql
mkdir /mnt/workspace/postgresql/9.6
mkdir /mnt/workspace/postgresql/9.6/main


# for my Docker Image
#cd /home/croeder
#rm -rf test.old
#mv test test.old
#tar xzf /media/sf_ubuntu_share/test.tgz
# chmod -R 755 test
# chown -R croeder test
#cd test

yum info docker > /dev/null
if [[ $? = !0 ]]; then
    yum install docker
fi
yum info docker > /dev/null
if [[ $? = !0 ]]; then
    echo "can't install docker, bye"
    exit 1
fi


echo "studies"
tar xvzf studies.tgz
# Not all the studies are here as they aren't all for distribution,
# and some aren't available from where this gets built.

echo "DB image"
gunzip db.tar.gz
docker rmi -v -f db
docker load < db.tar

echo""
echo "Harmonization image"
gunzip harmonization_ui.tar.gz
docker rmi -f harmonization_ui
docker load < harmonization_ui.tar

echo ""
echo "starting..."
#docker-compose up
/mnt/workspace/docker-compose up

