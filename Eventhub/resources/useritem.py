from flask_restful import Resource, Api, reqparse

from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)

from sqlalchemy.exc import IntegrityError
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, abort, Response, current_app
from Eventhub import db
from ..models import Event,LoginUser, User, LoginUser
from ..utils import InventoryBuilder, MasonBuilder, create_user_error_response
import json
from jsonschema import validate, ValidationError

LINK_RELATIONS_URL = "/eventhub/link-relations/"
USER_PROFILE = "/profiles/user/"
ERROR_PROFILE = "/profiles/error/"
MASON = "application/vnd.mason+json"
EVENT_PROFILE = "/profiles/EVENT/"



class UserItem(Resource):
    """
    Resource class for representing particular user
    """
    api = Api(current_app)

    def get(self, id):
    # """
    # get specific information for particular user
    # Parameters:
    #     - id: Integer, id of user
    # """
        print(id)
        id = int(id)
        api = Api(current_app)
        User.query.all()
        db_user = User.query.filter_by(id=id).first()
        print(db_user)
        
        db_loginuser = LoginUser.query.filter_by(id=id).first()
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
            return create_user_error_response(404, "Not found",
                                         "No user was found with the id {}".format(
                                             id)
                                         )
                                        
        body = InventoryBuilder(
            id=db_user.id,
            name=db_user.name,
            location=db_user.location,
            username = db_loginuser.username,
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
    # """
    # modify specific information for particular user
    # Parameters:
    #     - id: Integer, id of user
    # """
        api = Api(current_app)
        if not request.json:
            return create_user_error_response(415, "Unsupported media type",
                                         "Requests must be JSON"
                                         )
        try:
            validate(request.json, InventoryBuilder.user_schema())
        except ValidationError as e:
            return create_user_error_response(400, "Invalid JSON document", str(e))

        user = User(
            name=request.json["name"],
            location=request.json["location"]

        )

        db_user = User.query.filter_by(id=id).first()
        if db_user is None:
            return create_user_error_response(404, "Not found",
                                         "No product was found with the id {}".format(
                                             id)
                                         )


        db_user.id = id
        db_user.name = user.name
        db_user.location = user.location
        db.session.commit()

        return Response(status=204, headers={
            "Location": api.url_for(UserItem, id=id)
        })

    def delete(self, id):
    # """
    # delete specific information for particular user
    # Parameters:
    #     - id: Integer, id of user
    # """
    #     '''
    #     user = User(
    #         id=request.json["id"]
    #     )
        
    #     loginUser = LoginUser(
    #         id=request.json["id"]
    #     )

    #     db_user = User.query.filter_by(id=id).first()
    #     loginUser = LoginUser.query.filter_by(id=id).first()
    #     '''
        api = Api(current_app)
        user=db.session.query(LoginUser).get(id)


        if user is None:
            return create_user_error_response(404, "Doesn't exists",
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


parser = reqparse.RequestParser()
parser.add_argument('username', help = 'This field cannot be blank', required = True)
parser.add_argument('password', help = 'This field cannot be blank', required = True)



class UserLogin(Resource):
    def post(self):
        
        data = parser.parse_args()
        
        
        current_user = LoginUser.query.filter_by(username=data['username']).first()
        print(current_user.password_hash)

        if not current_user:
            return {'message': 'User {} doesn\'t exist'.format(data['username'])}
        
        if LoginUser.verify_hash(data['password'], current_user.password_hash):
            access_token = create_access_token(identity = data['username'])
            return {
                'message': 'Logged in as {}'.format(current_user.username),
                'access_token': access_token
                }
        else:
            return {'message': 'Wrong credentials'}


