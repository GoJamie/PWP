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
    time = db.Column(db.DateTime, nullable=True)
    picture = db.Column(db.String(256), nullable=True)
    name = db.Column(db.String(32), nullable=False, unique=True)
    location = db.Column(db.String(32), nullable=False, unique=True)
    event_id = db.Column(db.Integer, db.ForeignKey("event.id"))
    event = db.relationship("Event", back_populates="creator")


users = db.Table("joinedusers",
                 db.Column("user_id", db.Integer, db.ForeignKey(
                           "user.id"), primary_key=True),
                 db.Column("event_id", db.Integer, db.ForeignKey(
                           "event.id"), primary_key=True)
                 )

# @app.route("/user/add/", methods=["POST"])
# def add_user():
#     # This branch happens when client submits the JSON document

#     if not request.content_type == 'application/json':
#         return 'Request content type must be JSON', 415

#     try:

#         name = request.json["name"]
#         location = request.json["location"]
#         exist = User.query.filter_by(name=name).first()

#         if (exist == None):
#             pro = User(
#                 name=name,
#                 location=location

#             )
#             db.session.add(pro)
#             db.session.commit()
#             return "successful", 201
#         elif (exist != None):
#             return "Handle already exists", 409
#         else:
#             abort(404)
#     except (KeyError, ValueError, IntegrityError):

#         abort(400)

#     except (TypeError):
#         return 'Request content type must be JSON', 415


db.create_all()
