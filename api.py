#!/usr/bin/python3
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import database_exists, create_database, drop_database
import os
import datetime

app = Flask(__name__)
CORS(app)

# set up environmental variables
def get_env_variable(name):
    try:
        return os.environ[name]
    except KeyError:
        message = "Expected environment variable '{}' not set.".format(name)
        raise Exception(message)

def serialize_datetime(value):
    """Deserialize datetime object into string form for JSON processing."""
    if value is None:
        return None
    return [value.strftime("%Y-%m-%d"), value.strftime("%H:%M:%S")]

POSTGRES_URL = get_env_variable("POSTGRES_URL")
POSTGRES_USER = get_env_variable("POSTGRES_USER")
POSTGRES_PW = get_env_variable("POSTGRES_PW")
POSTGRES_DB = get_env_variable("POSTGRES_DB")

# connect to database
#DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(user=POSTGRES_USER,pw=POSTGRES_PW,url=POSTGRES_URL,db=POSTGRES_DB)
DB_URL = 'postgresql+psycopg2://{url}/{db}'.format(user=POSTGRES_USER,pw=POSTGRES_PW,url=POSTGRES_URL,db=POSTGRES_DB)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # silence the deprecation warning

# define database and schema
db = SQLAlchemy(app)

class Click(db.Model):

    __tablename__ = 'clickyTable'

    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime)
    hold = db.Column(db.Integer)
    latency = db.Column(db.Integer)
    side = db.Column(db.String)

    def __init__(self, time, hold, latency, side):
        self.time = time
        self.hold = hold
        self.latency = latency
        self.side = side

    @property
    def serialize(self):
       """Return object data in easily serializable format"""
       return {
           'id': self.id,
           'time': serialize_datetime(self.time),
           'hold': self.hold,
           'latency': self.latency,
           'side': self.side,
        }

api = Api(app)

# reset database
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

# test add a row
@app.cli.command('add')
def test_add():
    ms = 1564918545446
    time = datetime.datetime.fromtimestamp(ms/1000.0)
    click = Click(time=time, hold='100', latency='200', side='L')
    db.session.add(click)
    db.session.commit()
    print("Added!")

class Clicks(Resource):
    def get(self):

        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        # default query is last 100 keystrokes
        if (start_date == None or end_date == None):
            q = Click.query.order_by(Click.id.desc()).limit(100).all()

        # query for keystrokes between the given dates (inclusive)
        else:
            # convert from string to datetime
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
            end_date += datetime.timedelta(days=1)

            q = Click.query.filter(Click.time >= start_date).filter(Click.time <= end_date)

        clicks=[i.serialize for i in q]
        resp = jsonify(clicks)

        return resp

    def post(self):

        req = request.get_json()

        time = req['time']
        hold = req['hold']
        latency = req['latency']
        side = req['side']

        num_new_clicks = len(time)

        # arrays must be same length
        if num_new_clicks != len(hold) or num_new_clicks != len(latency) or num_new_clicks != len(side):
            return {'status': 400}

        for i in range(num_new_clicks):
            date = datetime.datetime.fromtimestamp(time[i]/1000.0)
            click = Click(time=date, hold=hold[i], latency=latency[i], side=side[i])
            db.session.add(click)
        
        db.session.commit()
        return {'status': 200}

api.add_resource(Clicks, '/')

if __name__ == '__main__':
    app.run()