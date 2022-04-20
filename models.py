from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

basedir = os.path.abspath(os.path.dirname(__file__))    
database_path = 'postgresql://postgres@localhost:5432/mydatabase'

db = SQLAlchemy()


def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.secret_key = os.urandom(32)
    db.app = app
    db.init_app(app)
    db.create_all()



# DONE: implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show (db.Model):
    __tablename__ = 'show'
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey("artist.id"))
    venue_id = db.Column(db.Integer, db.ForeignKey("venue.id"))
    start_time=db.Column(db.DateTime)
    

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.String)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship("Show", backref = "venue", lazy = True) 

# DONE: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500), unique=True)
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.String)
    seeking_description = db.Column(db.String(500))
