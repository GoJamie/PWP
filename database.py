import math
import os
import json
from flask import Flask, request, abort, jsonify, url_for
from passlib.apps import custom_app_context as pwd_context

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


users = db.Table("joinedusers",
                 db.Column("user_id", db.Integer, db.ForeignKey(
                           "user.id"), primary_key=True),
                 db.Column("event_id", db.Integer, db.ForeignKey(
                           "event.id"), primary_key=True)
                 )

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False, unique=True)
    description = db.Column(db.String(256), nullable=False)
    history = db.Column(db.Boolean, nullable=False)
    place = db.Column(db.String(32), nullable=True)
    time = db.Column(db.DateTime, nullable=True)
    creator = db.relationship("User", back_populates="events")
    creator_id = db.Column(db.Integer,db.ForeignKey("user.id"))
    joined_users = db.relationship("User", secondary=users, back_populates="joined_events")

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    picture = db.Column(db.String(256), nullable=True)
    name = db.Column(db.String(32), nullable=False, unique=True)
    location = db.Column(db.String(32), nullable=True, unique=False)
    events = db.relationship("Event", back_populates="creator")
    loginuser = db.relationship("LoginUser", back_populates='user')
    joined_events = db.relationship("Event",secondary=users,back_populates="joined_users")

# model for logining in, going go hash the password with hash_password methods and also verify the password with verify_password
class LoginUser(db.Model):
    id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    username = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(128))
    user = db.relationship("User",back_populates='loginuser',uselist=False)

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)



# @app.route('/api/users/', methods=['POST'])
# def new_user():
#     username = request.json.get('username')
#     password = request.json.get('password')
#     if username is None or password is None:
#         abort(400)  # missing arguments
#     if LoginUser.query.filter_by(username=username).first() is not None:
#         abort(400)  # existing user
#     user = LoginUser(username=username)
#     user.hash_password(password)
#     db.session.add(user)
#     db.session.commit()
#     return jsonify({'username': user.username, 'password': user.password_hash}), 201

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
