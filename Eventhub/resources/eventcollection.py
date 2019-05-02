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
    """
    Resource class for representing all events
    """
    def get(self):
        """
        # get information as follows
        # Information:
        #     - id: Integer, id of event
        #     - name: String, name of event
        #     - description: String, description of event
        #     - place: String, place of event
        #     - time: DataTime, time of event
        #     - creator_id: Integer, creator's id of event
        #     - join_users: users_id, Integer, id of user
        #                   users_name, String, name of user
        # Response:
        #     - 400: Found something else and get KeyError and ValueError
        #     - 200: Return information of all events (returns a Mason document)
        """
        api = Api(current_app)
        
        try:
            events = Event.query.all()
            body = InventoryBuilder(items=[])

            for j in events:
                if(j.creator != None):
                        
                    creator_user = {}

                    creator_user["id"] = j.creator.id
                    
                    creator_user["name"] = j.creator.name
                    joined_users = []
                    for i in j.joined_users:
                        user = {}
                        user["id"] = i.id
                        user["name"] = i.name
                        joined_users.append(user)
                        
                    item = MasonBuilder(
                        id=j.id, name=j.name, description=j.description, place=j.place, time=j.time,creator=creator_user, joined_users=joined_users)
                    item.add_control("self", api.url_for(
                        EventItem, id=j.id))
                    item.add_control("profile", "/profiles/event/")
                    body["items"].append(item)
                
            body.add_namespace("eventhub", LINK_RELATIONS_URL)
            body.add_control_all_events()
            body.add_control_add_event()

            return Response(json.dumps(body), 200, mimetype=MASON)
        except (KeyError, ValueError):
            abort(400)

    def post(self):
    """
    # post information for new event 
    # Parameters:
    #     - name: String, name of event
    #     - description: String, description of event
    #     - place: String, place of event
    #     - creator_id: Integer, creator's id of event
    # Response:
    #     - 415: create_event_error_response and alert "unsupported media type and Requests must be JSON"
    #     - 400: create_event_error_response and alert "Invalid JSON document" 
    #     - 409: create_event_error_response and alert "Already exists Event with id '{}' already exists."
    #     - 201: success
    """
        api = Api(current_app)
        if not request.json:
            return create_event_error_response(415, "Unsupported media type",
                                               "Requests must be JSON"
                                               )

        
        try:
            validate(request.json, InventoryBuilder.event_schema())
        except ValidationError as e:
            return create_event_error_response(400, "Invalid JSON document", str(e))
        
        user = User.query.filter_by(id=request.json["creatorId"]).first()
      
        event = Event(
            name = request.json["name"],
            description = request.json["description"],
            place = request.json["place"],
            creator_id = request.json["creatorId"]

        )

        event.creator = user
    
        events = Event.query.all()
        
        event.id = len(events) + 1

        try:

            body = InventoryBuilder()
            db.session.add(event)
            db.session.commit()
            print(api.url_for(EventItem, id=event.id))
                
            events = Event.query.all()
            
            event.id = len(events)

        except IntegrityError:
            return create_event_error_response(409, "Already exists",
                                               "Event with id '{}' already exists.".format(event.id)
                                               )
    
        return Response(status=201, headers={
            "Location": api.url_for(EventItem, id=event.id)
        
        })
