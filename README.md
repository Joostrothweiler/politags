# Politags (Beta v0.2)

Current work is for Beta version (Mar 15th)

## Code characteristics

* Directories
    * app
        * commands
        * models
        * modules
    * tests
    * data_resources
* Includes test framework (`py.test` and `tox`)
* Includes database migration framework (`alembic`)

## Setting up a development environment

Use Docker.

    docker-compose build
    docker-compose up

# Configuration

Copy the `local_settings_example.py` file to `local_settings.py`.

    cp app/local_settings_example.py app/local_settings.py

Edit the `local_settings.py` file.

## Initializing the Database

    # Create DB using Alembic migrations:
    python manage.py db upgrade
    
Ones you change something in the database, run:

    python manage.py db migrate
    
and

    python manage.py db upgrade

## Running the app

    # Start the Flask development web server
    docker-compose -f docker-compose.yml -f docker-compose-dev.yml up

Point your web browser to http://localhost:5555/ for the app
and http://localhost:9999/ for db adminer


    # To access the bash in docker:
    docker exec -it politags_web_1 bash
    
    # To create the database in bash
    python manage.py db migrate
    python manage.py db upgrade
    python manage.py init_db


## Running the automated tests

    # Start the Flask development web server
    py.test tests/

    # Or if you have Fabric installed:
    fab test
