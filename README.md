# Politags (Alpha v0.0)

Current work is for Alpha version (Jan 15th)

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

# Configuring SMTP

Copy the `local_settings_example.py` file to `local_settings.py`.

    cp app/local_settings_example.py app/local_settings.py

Edit the `local_settings.py` file.

## Initializing the Database

    # Create DB tables and populate the roles and users tables
    python manage.py init_db

## Running the app

    # Start the Flask development web server
    docker-compose up

Point your web browser to http://localhost:5555/ for the app
and http://localhost:9999/ for adminer

To access the bash in docker:
docker exec -it _service_ bash

## Running the automated tests

    # Start the Flask development web server
    py.test tests/

    # Or if you have Fabric installed:
    fab test
