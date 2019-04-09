from flask_restful import Resource, Api


from sqlalchemy.exc import IntegrityError
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, abort, Response, current_app
from .useritem import UserItem
from ..models import Event,LoginUser, User
from ..utils import InventoryBuilder, MasonBuilder, create_user_error_response
import json
from Eventhub import db
from jsonschema import validate, ValidationError

LINK_RELATIONS_URL = "/eventhub/link-relations/"
USER_PROFILE = "/profiles/user/"
ERROR_PROFILE = "/profiles/error/"
MASON = "application/vnd.mason+json"

USER_PROFILE = "/profiles/USER/"
ERROR_PROFILE = "/profiles/error/"


class EventsByUser(Resource):

    def get(self, id):
        api = Api(current_app)

        try:
            
            events = Event.query.all()
            for j in events:
                joined_users = j.joined_users
                print(joined_users)
            body = InventoryBuilder(items=[])
            return Response(json.dumps(body), 200, mimetype=MASON)
        except (KeyError, ValueError):
            abort(400)
