#!/usr/bin/python3
from flask import Flask, request
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import database_exists, create_database, drop_database
import os

app = Flask(__name__)

def get_env_variable(name):
    try:
        return os.environ[name]
    except KeyError:
        message = "Expected environment variable '{}' not set.".format(name)
        raise Exception(message)

# the values of those depend on your setup
POSTGRES_URL = get_env_variable("POSTGRES_URL")
POSTGRES_USER = get_env_variable("POSTGRES_USER")
POSTGRES_PW = get_env_variable("POSTGRES_PW")
POSTGRES_DB = get_env_variable("POSTGRES_DB")

DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(user=POSTGRES_USER,pw=POSTGRES_PW,url=POSTGRES_URL,db=POSTGRES_DB)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # silence the deprecation warning

db = SQLAlchemy(app)


class Click(db.Model):

    __tablename__ = 'clickyTable'

    id = db.Column(db.Integer, primary_key=True)
    clicks = db.Column(db.Integer)

    def __init__(self, clicks):
        self.clicks = clicks



api = Api(app)
clicks = []

@app.cli.command('resetdb')
def resetdb_command():

    if database_exists(DB_URL):
        print('Deleting database...')
        drop_database(DB_URL)
    if not database_exists(DB_URL):
        print('Creating database...')
        create_database(DB_URL)

    print('Creating tables...')
    db.create_all()
    print('Done!')


@app.cli.command('add')
def test_add():
    click = Click(clicks=100)
    db.session.add(click)
    db.session.commit()
    print("added")


class HelloWorld(Resource):
    def get(self):
        print('flask GET')
        json = {'all_clicks': clicks}
        return json

    def post(self):
    	print("flask POST")
    	print(request.get_json())
    	new_clicks = request.get_json()['new_clicks']
    	print(new_clicks)
    	clicks.extend(new_clicks)
    	return {'new_clicks': new_clicks}

api.add_resource(HelloWorld, '/')

if __name__ == '__main__':
    app.run()