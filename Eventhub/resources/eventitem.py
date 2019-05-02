from flask_restful import Resource, Api


from sqlalchemy.exc import IntegrityError
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, abort, Response, current_app
from Eventhub import db
from ..models import Event,LoginUser, User
from ..utils import InventoryBuilder, MasonBuilder, create_event_error_response
import json
from jsonschema import validate, ValidationError


LINK_RELATIONS_URL = "/eventhub/link-relations/"
USER_PROFILE = "/profiles/user/"
ERROR_PROFILE = "/profiles/error/"
MASON = "application/vnd.mason+json"
EVENT_PROFILE = "/profiles/EVENT/"

class EventItem(Resource):
    """
    Resource class for representing particular event
    """
    def get(self, id):
    """
    # get specific information for particular event 
    # Parameters:
    #     - id: Integer, id of event
    # Response:
    #     - 404: create_event_error_response and alert "Not found No event was found with the id {}"
    #     - 200: success
    # Information:
    #     - name: String, name of event
    #     - description: String, description of event
    #     - place: String, place of event
    #     - time: DataTime, time of event
    #     - creator_id: Integer, creator's id of event
    #     - join_users: users_id, Integer, id of user
    #                   users_name, String, name of user
    """
        api = Api(current_app)
        db_event = Event.query.filter_by(id=id).first()
        if db_event is None:
            return create_event_error_response(404, "Not found",
                                         "No event was found with the id {}".format(
                                             id)
                                         )
        
        if db_event.creator is None:
            return create_event_error_response(404, "Not found",
                                         "No event was found with the id {}".format(
                                             id)
                                         )

        joined_users = db_event.joined_users
        users = []
        for i in joined_users:
            user = {}
            user["name"] = i.name
            user["id"] = i.id
            item = MasonBuilder(id=i.id,name=i.name)
            users.append(item)
        body = InventoryBuilder(
            id=db_event.id,
            name=db_event.name,
            description=db_event.description,
            place=db_event.place,
            time=db_event.time,
            joined_users = users
        )
        body.add_namespace("eventhub", LINK_RELATIONS_URL)
        body.add_control("self", api.url_for(EventItem, id=id))
        body.add_control("profile", EVENT_PROFILE)
        body.add_control_delete_event(id)
        body.add_control_edit_event(id)
        body.add_control_all_events()
        return Response(json.dumps(body), 200, mimetype=MASON)

    def put(self, id):
    """
    # modify specific information for particular event 
    # Parameters:
    #     - id: Integer, id of event
    #     - name: String, name of event
    #     - description: String, description of event
    #     - place: String, place of event
    #     - time: DataTime, time of event
    # Response:
    #     - 415: create_event_error_response and alert "Unsupported media type Requests must be JSON"
    #     - 404: create_event_error_response and alert "Not found No event was found with the id {}"
    #     - 400: create_event_error_response and alert "Invalid JSON document"
    #     - 204: success
    """
        api = Api(current_app)
        if not request.json:
            return create_event_error_response(415, "Unsupported media type",
                                         "Requests must be JSON"
                                         )

        event = Event(
            id=id,
            name=request.json["name"],
            place=request.json["place"],
            time=request.json["time"],
            description=request.json["description"],
        )

        db_event = Event.query.filter_by(id=id).first()
        if db_event is None:
            return create_event_error_response(404, "Not found",
                                         "No event was found with the id {}".format(
                                             id)
                                         )

        try:
            validate(request.json, InventoryBuilder.user_schema())
        except ValidationError as e:
            return create_event_error_response(400, "Invalid JSON document", str(e))

        
        db_event.id = event.id
        db_event.name = event.name
        db_event.place = event.place
        
        db_event.description = event.description
        db.session.commit()

        return Response(status=204, headers={
            "Location": api.url_for(EventItem, id=id)
        })
