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
from .eventitem import EventItem

LINK_RELATIONS_URL = "/eventhub/link-relations/"
USER_PROFILE = "/profiles/user/"
ERROR_PROFILE = "/profiles/error/"
MASON = "application/vnd.mason+json"

USER_PROFILE = "/profiles/USER/"
ERROR_PROFILE = "/profiles/error/"
EVENT_PROFILE = "/profiles/EVENT/"

class EventsByUser(Resource):
    """
    Resource class for representing all events for particular user
    """
    def get(self, user_id):
    # """
    # get all events information for particular user 
    # Parameters:
    #     - id: Integer, id of event
    # """
        api = Api(current_app)
        body = InventoryBuilder(items=[])
        user = User.query.filter_by(id=user_id).first()
        if user is None:
            return create_user_error_response(404, "Not found",
                                        "No user was found with the id {}".format(
                                            user_id)
                                        )

        body["user"] = {"user_id":user.id,"name":user.name}
        body.add_namespace("eventhub", LINK_RELATIONS_URL)
        body.add_control("self", api.url_for(UserItem, id=user_id))
        body.add_control("profile", USER_PROFILE)
        body.add_control_delete_user(user_id)
        body.add_control_edit_user(user_id)
        body.add_control_all_users()        

        try:
            
            events = Event.query.all()
            for j in events:
                event_body = InventoryBuilder()
                event_body["id"] = j.id
                event_body["name"] = j.name
                event_body["creator_id"] = j.creator_id
                event_body["place"] = j.place
                event_body["time"] = j.time
                event_body["description"] = j.description
                users = []
                joined_users = j.joined_users
                for i in joined_users:
                                
                    db_loginuser = LoginUser.query.filter_by(id=i.id).first()

                    user = {}
                    user["id"] = i.id
                    user["name"] = i.name
                    user["username"] = db_loginuser.username
                    users.append(user)
                event_body["joined_users"] = users
                event_body.add_namespace("eventhub", LINK_RELATIONS_URL)
                event_body.add_control("self", api.url_for(EventItem, id=j.id))
                event_body.add_control("profile", EVENT_PROFILE)
                event_body.add_control_delete_event(j.id)
                event_body.add_control_edit_event(j.id)
                event_body.add_control_all_events()
                body["items"].append(event_body)            
            return Response(json.dumps(body), 200, mimetype=MASON)
        except (KeyError, ValueError):
            abort(400)
