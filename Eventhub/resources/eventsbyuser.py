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
            users = User.query.all()
            body = InventoryBuilder(items=[])
            for j in users:
                item = MasonBuilder(id=j.id, name=j.name, place=j.location, joined_events=j.joined_events)
                item.add_control("self", api.url_for(
                    UserItem, id=j.id))
                item.add_control("profile", "/profiles/user/")
                body["items"].append(item)
            body.add_namespace("eventhub", LINK_RELATIONS_URL)
            body.add_control_all_users()
            body.add_control_add_user()
            print(body)

            return Response(json.dumps(body), 200, mimetype=MASON)
        except (KeyError, ValueError):
            abort(400)
