#/usr/bin/env bash

# get and install pip, then use it to install pandas and sqlalchemy
# https://packaging.python.org/tutorials/installing-packages/

sudo pip install pandas
sudo pip install sqlalchemy
sudo pip install psycopg2
sudo pip install --upgrade "git+https://bitbucket.org/hfclinicaldata/heart_data.git"
