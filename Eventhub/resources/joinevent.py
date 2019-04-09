from flask_restful import Resource, Api

from sqlalchemy.exc import IntegrityError
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, abort, Response, current_app
from Eventhub import db
from ..models import Event,LoginUser, User
from ..utils import InventoryBuilder, MasonBuilder, create_user_error_response
import json
from jsonschema import validate, ValidationError
from .eventsbyuser import EventsByUser

LINK_RELATIONS_URL = "/eventhub/link-relations/"
USER_PROFILE = "/profiles/user/"
ERROR_PROFILE = "/profiles/error/"
MASON = "application/vnd.mason+json"
EVENT_PROFILE = "/profiles/EVENT/"


class JoinEvent(Resource):

    def put(self, user_id, event_id):
        api = Api(current_app)
        if not request.json:
            return create_user_error_response(415, "Unsupported media type",
                                         "Requests must be JSON"
                                         )
        event = Event.query.filter_by(id=event_id).first()
        user = User.query.filter_by(id=user_id).first()
        if user is None:
            return create_error_response(404, "Not found",
                                         "No product was found with the id {}".format(
                                             id)
                                         )

        try:
            event.joined_users.append(user)
            db.session.commit()
        except IntegrityError:
            return create_error_response(409, "Already exists",
                                         "user with name '{}' already exists.".format(
                                             request.json["handle"])
                                         )

        return Response(status=204, headers={
            "Location": api.url_for(EventsByUser, user_id=user_id)
        })