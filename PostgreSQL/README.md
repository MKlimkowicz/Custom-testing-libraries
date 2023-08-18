# PostgreSQL Testing Project

This repository contains a simple example project that demonstrates how to interact with a PostgreSQL database using Python and how to test these interactions. It includes Docker configurations to create a reproducible environment.

## Project Structure

- `main.py`: Contains the main functions for interacting with the PostgreSQL database.
- `models.py`: Contains the SQL commands to create and manipulate the database tables.
- `test_db.py`: Contains the unit tests for the functions in `main.py`.
- `Dockerfile`: Docker configuration to build the Python environment.
- `docker-compose.yml`: Docker Compose configuration to set up and run the PostgreSQL service.
- `requirements.txt`: Lists the Python packages that the project depends on.
- `run.sh`: A shell script that runs the Python test script.
- `wait-for.sh`: A shell script that waits for the PostgreSQL service to be ready before running the Python script.

## Installation and Setup

git clone <repository-url>

## Navigate to the project directory

cd <project-directory>

## Build and run the Docker Compose setup and tests

./run.sh

## To modify Postgres image, initial wait or check interval

./run.sh postgres:13 15 3

if you want to modify just Postgres image

./run.sh postgres:12 "" ""
