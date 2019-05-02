from flask_restful import Resource, Api

from sqlalchemy.exc import IntegrityError
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, abort, Response, current_app
from Eventhub import db
from ..models import Event,LoginUser, User
from ..utils import InventoryBuilder, MasonBuilder, create_user_error_response, create_event_error_response
import json
from jsonschema import validate, ValidationError
from .eventsbyuser import EventsByUser
from .eventitem import EventItem

LINK_RELATIONS_URL = "/eventhub/link-relations/"
USER_PROFILE = "/profiles/user/"
ERROR_PROFILE = "/profiles/error/"
MASON = "application/vnd.mason+json"
EVENT_PROFILE = "/profiles/EVENT/"


class JoinEvent(Resource):
    """
    Resource class for representing user who wants to modify the status of event
    """
    def put(self, user_id, event_id):
        """
        # modify the information of joining event 
        # Parameters:
        #     - user_id: Integer, id of user
        #     - event_id: Integer, id of event
        # Response:
        #     - 404: create_event_error_response and alert "Not found No event was found with the id {}"
        #     - 404: create_user_error_response and alert "Not found No user was found with the id {}"
        #     - 409: create_event_error_response and alert "Already exists event with id '{}' already exists."
        #     - 409: create_uesr_error_response and alert "Already exists user with id '{}' already exists."
        #     - 204: success to edit
        """    
        api = Api(current_app)
        event = Event.query.filter_by(id=event_id).first()
        if event is None:
            return create_event_error_response(404, "Not found",
                                         "No event was found with the id {}".format(
                                             event_id)
                                         )

        event = Event.query.filter_by(id=event_id).first()
        for i in event.joined_users:
            if i.id == int(user_id):
                return create_user_error_response(409, "Already exists",
                                            "user with id '{}' already exists.".format(
                                                i.id)
                                            )
        user = User.query.filter_by(id=user_id).first()
        if user is None:
            return create_user_error_response(404, "Not found",
                                         "No user was found with the id {}".format(
                                             id)
                                         )

        try:
            event.joined_users.append(user)
            db.session.commit()
        except IntegrityError:
            return create_user_error_response(409, "Already exists",
                                         "user with name '{}' already exists.".format(
                                             user.id)
                                         )

        return Response(status=204, headers={
            "Location": api.url_for(EventsByUser, user_id=user_id)
        })

    def delete(self, user_id, event_id):
        """
        # Delete the information of joined event 
        # Parameters:
        #     - user_id: Integer, id of user
        #     - event_id: Integer, id of event
        # Response:
        #     - 404: create_event_error_response and alert "Doesn't exists event with id '{}' doesn't exist."
        #     - 404: create_user_error_response and alert "Doesn't exists user with id '{}' doesn't exist."
        #     - 404: create_error_response and alert "Doesn't exists user with id '{}' doesn't exist in event with id '{}' 
        #     - 204: success to delete
        """  
        api = Api(current_app)

        event = Event.query.filter_by(id=event_id).first()
        user=db.session.query(User).get(user_id)


        if user is None:
            return create_user_error_response(404, "Doesn't exists",
                                         "user with id '{}' doesn't exist.".format(
                                             user_id)
                                         )

        if event is None:
            return create_event_error_response(404, "Doesn't exists",
                                         "event with id '{}' doesn't exist.".format(
                                             event_id)
                                         )

        user_not_event = False

        for j in event.joined_users:
            if j.id == user_id:
                event.joined_users.remove(j)
                user_not_event = True

        if user_not_event:
            return create_error_response(404, "Doesn't exists",
                                         "user with id '{}' doesn't exist in event with id '{}'.".format(
                                             user_id, event_id)
                                         )

        db.session.commit()

        return Response(status=204, headers={
            "Location": api.url_for(EventItem, id=event_id)
        })