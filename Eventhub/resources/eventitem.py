from flask_restful import Resource, Api


from sqlalchemy.exc import IntegrityError
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, abort, Response, current_app
from Eventhub import db
from ..models import Event,LoginUser, User
#from .eventcollection import EventCollection
#from ..utils import InventoryBuilder, MasonBuilder, create_event_error_response
import json
from jsonschema import validate, ValidationError


LINK_RELATIONS_URL = "/eventhub/link-relations/"
USER_PROFILE = "/profiles/user/"
ERROR_PROFILE = "/profiles/error/"
MASON = "application/vnd.mason+json"
EVENT_PROFILE = "/profiles/EVENT/"

class EventItem(Resource):
    api = Api(current_app)
    def get(self, id):
    
        db_event = Event.query.filter_by(id=id).first()
        if db_event is None:
            return create_error_response(404, "Not found",
                                         "No event was found with the id {}".format(
                                             id)
                                         )

        body = InventoryBuilder(
            id=db_event.id,
            name=db_event.name,
            description=db_event.description,
            place=db_event.place,
            time=db_event.time
        )
        body.add_namespace("eventhub", LINK_RELATIONS_URL)
        body.add_control("self", api.url_for(EventItem, id=id))
        body.add_control("profile", Event_PROFILE)
        body.add_control_delete_event(id)
        body.add_control_edit_event(id)
        body.add_control_all_event()
        print("success!")
        return Response(json.dumps(body), 200, mimetype=MASON)
    
        return 
    def put(self, handle):
        return
