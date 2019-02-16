import math
import os
import json
from flask import Flask, request,  abort

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy.engine import Engine
from sqlalchemy import event
from datetime import datetime
app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False, unique=True)
    description = db.Column(db.String(256), nullable=False)
    history = db.Column(db.Boolean, nullable=False)
    place = db.Column(db.String(32), nullable=True)
    time = db.Column(db.DateTime, nullable=True)

    creator = db.relationship(
        "User", back_populates="event", uselist=False)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime, nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey("event.id"))
    event = db.relationship("Event", back_populates="creator")


users = db.Table("joinedusers",
                 db.Column("user_id", db.Integer, db.ForeignKey(
                           "user.id"), primary_key=True),
                 db.Column("event_id", db.Integer, db.ForeignKey(
                           "event.id"), primary_key=True)
                 )

db.create_all()
