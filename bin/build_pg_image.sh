#!/usr/bin/env bash
set -e

# build_pg_image
#
# a script for use when bashing on how to get postgres running with an external
# data directory in Docker. This is a snipper of the larger script build_docker.sh

rm ~/ubuntu_share/test/db.tar.gz

docker build -f Dockerfile.postgresql -t db .
docker save db > db.tar
gzip -f db.tar
cp db.tar.gz ~/ubuntu_share/test


