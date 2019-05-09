# PWP SPRING 2019
# Event API
# Group information
* Student 1. Bangju Wang wangbangju@outlook.com
* Student 2. Nechir Salimi nechir123@hotmail.com
* Student 3. Hao Ban s8125867@qq.com

# Requirements

This project requires `flask`, `pysqlite3`, `flask-sqlalchemy`, `flask-restful`, `jsonschema` 

For testing, `pytest` is need to do database_test and resource_test.

All dependencies can be installed using `pip install` command followed by the name of library.    

# Database setup

## Creating and populating the database

The database can be created by running the command  `set FLASK_APP=Eventhub` from the directory above the PWP folder. In `__init__.py`, we create app according to the configuration by `create_app`.

Note that you need to set environment as `set FLASK_ENV=development`. And then, you can use `flask run` to initialize the database.

## Testing Database

After setting database, we use `db_test.py` in `tests` folder to test database.

You can use command `pytest db_test.py` to test database.

## Running and testing the API

Before running and testing the API, you need to set `FLASK_APP=Eventhub` and `FLASK_ENV=development`, and run ti by using command `flask run`. We use `rs_test.py` in `tests` folder to test resource and API.

You can use command `pytest rs_test.py` to test API.

## Running the client

Before running the client, you need to install Node.js <a>https://nodejs.org/en/download/</a>. Then navigate to event-client and run  `npm install` for installing all the nesseccary dependencies.
When you have all dependencies then run `npm run start`. Make sure you already run the server.


