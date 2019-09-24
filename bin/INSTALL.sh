#!/usr/bin/env bash
APP_HOME=$PWD
set -e
#
# INSTALL.sh
# requires sudo privileges
# put the zip file somewhere, unzip and cd into harmonization, edit env.sh if you need to, 
# then run INSTALL.sh from the base harmonization directory where you would say bin/INSTALL.sh
#

function make_opt_local_harmonization {
    # empty /opt/local/harmonization tree
    mkdir opt_local_harmonization
    mkdir opt_local_harmonization/output
    mkdir opt_local_harmonization/deployment
    mkdir opt_local_harmonization/deployment/studies
    mkdir opt_local_harmonization/deployment/studies/PARADIGM
    mkdir opt_local_harmonization/deployment/studies/ATMOSPHERE
    mkdir opt_local_harmonization/deployment/studies/CORONA
    mkdir opt_local_harmonization/deployment/studies/CORONA/data
    
    touch opt_local_harmonization/deployment/studies/PARADIGM/test.csv
    touch opt_local_harmonization/deployment/studies/ATMOSPHERE/test.csv
    touch opt_local_harmonization/deployment/studies/CORONA/data/sample.csv
}






# Python3?
echo "Checking for Python3..."
python3 -V 2>&1 | grep "Python 3"
echo "...got it."
echo ""

echo "Installing packages for Python3..."
pip3 install -r requirements.txt &> pip3.log
echo "...got it."
echo ""

# PostgreSQL?
echo "Checking for PostgreSQL "
psql --version 2>&1 |  grep "(PostgreSQL)"
echo "...got it."
echo ""


# /opt/local?
if ! [ -d /opt/local ] ; then
    echo "Creating /opt/local"
    mkdir -p /opt/local
    echo "...got it."
fi

if ! [ -d /opt/local/harmonization ] ; then
    echo "Copying harmonization into /opt/local."
    make_opt_local_harmonization 
    mv $APP_HOME/opt_local_harmonization /opt/local/harmonization
    ls /opt/local/harmonization
    echo "...got it."
fi

# pause for stuff
echo ""
read -p "Pausing for file copy. Hit enter to continue."
echo ""
set +e
echo "Current DB variables:"
env | grep PG
set -e
echo ""
read -p "Pausing for edit bin/env.sh. Hit enter to continue."
. bin/env.sh



# Do we have a heart_db_v2?
echo "checking for heart_db_v2 database"
echo "\conninfo"  | psql
echo "\conninfo" | psql 2>&1  | grep heart_db_v2
echo "...got it."
echo ""

# OMOP?
echo "is OMOP in that database?"
echo "\d observation" | psql | grep observation_concept_id
echo "...got it."
echo ""


# concepts
echo "Loading new concepts."
cat sql/concept.sql | psql &> concept.log
echo "...loaded"
echo ""

# mappings
echo "Loading Mappings."
bin/load_mappings.sh  &> load_mappings.log
echo "...loaded"
echo ""

# start django
echo "Starting Django web server in the background. Logging to djanago.log."
echo "Consider running tail -f django.log in a second window."
cd django_harmonization
python3 manage.py runserver 0.0.0.0:8000 &> ../django.log &
cd ..
ls -l django.log
ps -aef | grep manage | grep python 
echo "...started"
echo ""

echo "OK, after a few seconds, point your broswer at http://localhost:8000/ui/pipeline.html"
echo "http://localhost:8000/ui/pipeline.html" | pbcopy
echo "The URL has been copied to your paste buffer."
read -p "Pausing.  Hit enter to continue."
echo ""

echo "Click \"Load Studies\", when complete (when \"running\" turns into \"COMPLETE\" next to the button), reload the browser window. (5 min.)"
read -p "Pausing.  Hit enter to continue."
echo ""

echo "Choose a study, CORONA. Click \"Migrate\". Watch for \"COMPLETE\" (4 min.)"
read -p "Pausing.  Hit enter to continue."
echo ""

echo "Click \"Calculate\". Watch for \"COMPLETE\" (1 min.)"
read -p "Pausing.  Hit enter to continue."
echo ""

echo "Select an extract configuration, under \"Study Choice\" select \"paradigm-atmosphere\"."
echo ""

echo "Select an extract configuration, under \"Study Choice\" select \"paradigm-atmosphere\"."
echo "Click  \"Extract\". Watch for \"COMPLETE\" below. (3 min.)"
echo "When it says complete, you're done.  The csv file is in /opt/local/harmonization/output."
read -p "Pausing.  Hit enter to continue. File line count and first three rows will follow."
echo ""
ls -l /opt/local/harmonization/output
wc -l /opt/local/harmonization/output/*.csv
