

# working on using django to build a UI for the harmonization project

Code assumes the following:
/opt/local/harmonization/deployment
    studies.tgz
    ohdsi.tgz
    backups


/opt/local/harmonization/output
    for generated CSV files

# README #

This README would normally document whatever steps are necessary to get your application up and running.

### What is this repository for? ###

* Quick summary
* Version
* [Learn Markdown](https://bitbucket.org/tutorials/markdowndemo)

### How do I get set up? ###

* Summary of set up
* Configuration
* Dependencies
     pip install --upgrade "git+https://bitbucket.org/hfclinicaldata/heart_data.git"
* Database configuration
* How to run tests
* Deployment instructions

### Contribution guidelines ###

* Writing tests
* Code review
* Other guidelines

### Who do I talk to? ###

* Repo owner or admin
* Other community or team contact

# LINKS
* Django https://www.djangoproject.com/
* https://docs.djangoproject.com/en/2.0/howto/legacy-databases/
* https://docs.djangoproject.com/en/2.0/intro/tutorial01/
* https://docs.djangoproject.com/en/2.0/topics/db/models/
* Django-REST http://www.django-rest-framework.org/
* http://www.django-rest-framework.org/tutorial/quickstart/

### TODO
* Authentication
* Multi-tenant, permissions, versioning, 
    ** a harmonization schema evolves, results a paper depends on requires a specific version and it needs to be accessible from static storage in perpituity
* Installs, Starter Database
   ** Vocabulary Update, additions to vocabulary
* Unit Test Pipeline
# There's a boot strapping problem where the UI needs to know about tables in a study before it can be used to define mappings. Need a better description TODO`:

