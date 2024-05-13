# Vibra Gaming Challenge

## Prerequisites

- Python 3.7+

- Poetry

- Docker and docker compose

## Common tasks

### Create virtual environment with dependencies

    python3 -m venv venv; source venv/bin/activate; poetry install; pip uninstall -y apiflask; pip install apiflask

### Specify development config (with debug mode on)

    export FLASK_ENV=development

### Run development flask server

    flask run

### Build docker image

    docker build .

### Run with docker compose

    docker-compose up --build

### Run migrations
    flask db upgrade

When running the migration:
- a new table named csv_data will be created.
- the CSV will be saved into the database.

### Run tests

    python3 -m unittest discover -s app -p '*tests.py'

## Steps to Follow to Search for the CSV:
    # call the GET endpoint in the browser; the response will be a <transaction_id> associated with a Redis key.
    http://0.0.0.0:5000/search-csv?name=<string>&city=<string>&quantity=<int>

    # take the Redis key (transaction_id) and call the endpoint that returns the records with applied filters.
    http://0.0.0.0:5000/redis/<transaction_id>

### Options:
- filter by name only.
- filter by city only.
- filter by quantity only.
- if no filters are applied, list all results.
- if the filters do not match, return an empty list.
