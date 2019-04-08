from flask_restful import Resource, Api


from sqlalchemy.exc import IntegrityError
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, abort, Response, current_app
from .eventitem import EventItem
from ..models import Event,LoginUser, User
from ..utils import InventoryBuilder, MasonBuilder, create_event_error_response
import json
from Eventhub import db
from jsonschema import validate, ValidationError

LINK_RELATIONS_URL = "/eventhub/link-relations/"
USER_PROFILE = "/profiles/user/"
ERROR_PROFILE = "/profiles/error/"
MASON = "application/vnd.mason+json"

EVENT_PROFILE = "/profiles/EVENT/"
ERROR_PROFILE = "/profiles/error/"


class EventCollection(Resource):

    def get(self):
        api = Api(current_app)

        print("11111")
        try:
            events = Event.query.all()
            body = InventoryBuilder(items=[])

            for j in events:
                user = {}
                user["id"] = j.creator.id
                
                user["name"] = j.creator.name

                item = MasonBuilder(
                    id=j.id, name=j.name, description=j.description, place=j.place, time=j.time,creator=user, joined_users=j.joined_users)
                item.add_control("self", api.url_for(
                    EventItem, handle=j.id))
                item.add_control("profile", "/profiles/event/")
                body["items"].append(item)
            body.add_namespace("eventhub", LINK_RELATIONS_URL)
            body.add_control_all_events()
            body.add_control_add_event()
            print(body)
            
            return Response(json.dumps(body), 200, mimetype=MASON)
        except (KeyError, ValueError):
            abort(400)

    def post(self):
        api = Api(current_app)
        if not request.json:
            return create_event_error_response(415, "Unsupported media type",
                                               "Requests must be JSON"
                                               )

        try:
            validate(request.json, InventoryBuilder.event_schema())
        except ValidationError as e:
            return create_event_error_response(400, "Invalid JSON document", str(e))
        
        loginuser = LoginUser(username='user-{}'.format(1))
        loginuser.hash_password('password')
        user = User(
        name='Bangju Wang')
        loginuser.user = user
        event = Event(
        name='PWP Meeting',
        description="Test event"
        )
        loginuser.user = user
        event.creator = user

        try:

            body = InventoryBuilder()
                    
            db.session.add(user)
            db.session.add(loginuser)
            db.session.add(event)
            db.session.commit()


            return Response(json.dumps(body), 201, mimetype=MASON)
        except IntegrityError:
            return create_event_error_response(409, "Already exists",
                                               "Product with handle '{}' already exists.".format("asasd")
                                               )

        return Response(status=201, headers={
            "Location": api.url_for(EventItem, id=request.json["id"])
        })
