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


class UserItem(Resource):

    api = Api(current_app)

    def get(self, id):
        api = Api(current_app)
        db_user = User.query.filter_by(id=id).first()
        events = Event.query.filter_by(creator_id=id).all()
        events_list = []
        for j in events:
            item = {}
            item["id"] = j.id
            item["name"] = j.name
            item["description"] = j.description
            item["place"] = j.place
            item["time"] = j.time
            events_list.append(item)

        if db_user is None:
            return create_error_response(404, "Not found",
                                         "No user was found with the id {}".format(
                                             id)
                                         )

        body = InventoryBuilder(
            id=db_user.id,
            name=db_user.name,
            location=db_user.location,
            Created_events =events_list
        )
        body.add_namespace("eventhub", LINK_RELATIONS_URL)
        body.add_control("self", api.url_for(UserItem, id=id))
        body.add_control("profile", USER_PROFILE)
        body.add_control_delete_user(id)
        body.add_control_edit_user(id)
        body.add_control_all_users()
        return Response(json.dumps(body), 200, mimetype=MASON)


    def put(self, id):
        if not request.json:
            return create_error_response(415, "Unsupported media type",
                                         "Requests must be JSON"
                                         )

        user = User(
            id=request.json["id"],
            name=request.json["name"],
            location=request.json["location"],

        )

        db_user = User.query.filter_by(id=id).first()
        if db_user is None:
            return create_error_response(404, "Not found",
                                         "No product was found with the id {}".format(
                                             id)
                                         )

        try:
            validate(request.json, InventoryBuilder.user_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))

        try:
            db_user.id = user.id
            db_user.name = user.name
            db_user.location = user.location
            db.session.add(db_user)
            db.session.commit()
        except IntegrityError:
            return create_error_response(409, "Already exists",
                                         "user with name '{}' already exists.".format(
                                             request.json["handle"])
                                         )

        return Response(status=204, headers={
            "Location": api.url_for(UserItem, id=request.json["id"])
        })

    def delete(self, id):
        '''
        user = User(
            id=request.json["id"]
        )
        
        loginUser = LoginUser(
            id=request.json["id"]
        )

        db_user = User.query.filter_by(id=id).first()
        loginUser = LoginUser.query.filter_by(id=id).first()
        '''
        api = Api(current_app)
        user=db.session.query(LoginUser).get(id)


        if user is None:
            return create_event_error_response(404, "Doesn't exists",
                                         "user with id '{}' doesn't exists.".format(id)
                                         )


        #db.session.delete(db_user)
        #db.session.commit()
        
        print(user)

        db.session.delete(user)
        db.session.commit()
    
        return Response(status=204, headers={
            "Location": api.url_for(UserItem, id=user.id)
        })
