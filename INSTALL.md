
# Prerequisites:
* Python3
* PostgreSQL 9.6
* an OHDSI starter database for CDM v5  and concepts DETAIL
** CDM  v6 has a set of scripts, ddl, available to create tables and sequences
** concepts or vocabulary are aviable through the OHDSI Athena project, the vocabularies chosen there are a good starter. Leave of RxNorm Extenstionssince they are huge and not used.
* csv files from studies
* an extract or archive from the git repo
* a user writable directory at /opt/local/harmonization/output
* studies at /opt/local/harmonization/studies
** study directories whose names are the same as the study_name field in the Study table

# Install and setup
* in the django_harmonization directory with manage.py in it start django
** python3 manage.py runserver 0.0.0.0:8000
* point a browser at 127.0.0.1:8000/ui/index.html
* select the "Run Pipeline" option
** Load Mapping
** Load Studies
** refresh the window

# Configure a study that is new to the system (UI TBD)
* add entries to study, study_files
* add mappings for the fields in the Person table: race, age, sex
* use UI to add more mappings for impore and export as described below

# Import data from a study
* choose a study that has been loaded
* in the lower group
** migrate
** calculate
* in the lowest group choose an extract study configuration
** extract

# Configure imports
* use the index link at the top of the page to get back to the main menu
* choose Define Harmonization Mappings (import)
* pick a study... DETAIL

# Configure locally calculated fields TBD

# Configure exports
* use the index link at the top of the page to get back to the main menu
* choose Define  Analysis Matrix (export)
* choose an extract_study configuration
* DETAIL
