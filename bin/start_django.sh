#!/usr/bin/env bash

# starts django
#
# This script lives in the bin directory which is next to
# the django_harmonization directory that is the home of 
# the application and contains manage.py. cd to there.

DIR=$(dirname $0 )
cd $DIR/../django_harmonization
python3 manage.py runserver 0.0.0.0:8000


