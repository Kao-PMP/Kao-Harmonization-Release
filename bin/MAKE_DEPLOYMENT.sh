#!/usr/bin/env bash

git checkout master
echo "Did  you COMMIT? this script pulls from git, not the working index"
echo "considering cleaning up tags from development."

# archive from git
DATE=$(date +%Y-%m-%d_%H-%M)
echo $DATE
TAG=harm_$DATE
git tag -a $TAG -m "delivery for $DATE"
DEP_PKG=harm_$DATE.zip 
GIT_REPO=/Users/christopherroeder/work/git/harmonization/django_harmonization
git archive --format=zip --output=$DEP_PKG $TAG $GIT_REPO





