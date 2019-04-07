from flask_restful import Resource, Api

from flask import Flask, request, abort, Response, current_app
from .eventitem import EventItem
from ..models import Event
from ..utils import InventoryBuilder, MasonBuilder
import json

LINK_RELATIONS_URL = "/eventhub/link-relations/"
USER_PROFILE = "/profiles/user/"
ERROR_PROFILE = "/profiles/error/"
MASON = "application/vnd.mason+json"

EVENT_PROFILE = "/profiles/EVENT/"
ERROR_PROFILE = "/profiles/error/"


class EventCollection(Resource):
    api = Api(current_app)
    def get(self):
        print("11111")
        try:
            events = Event.query.all()
            body = InventoryBuilder(items=[])

            for j in events:
                item = MasonBuilder(
                    id=j.id, name=j.name, description=j.description, place=j.place, time=j.time, creator=j.creator, joined_users=j.joined_users)
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
        if not request.json:
            return create_error_response(415, "Unsupported media type",
                                         "Requests must be JSON"
                                         )

        try:
            validate(request.json, InventoryBuilder.event_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))

        event = Event(
            id=request.json["id"],
            name=request.json["name"],
            description=request.json["description"]
            place=request.json["place"],
            time=request.json["time"],
            creator=request.json["creator"]
        )

        try:

            body = InventoryBuilder()
            db.session.add(event)
            db.session.commit()

            body.add_control("self", api.url_for(
                EventItem, id=event.id))

            return Response(json.dumps(body), 201, mimetype=MASON)
        except IntegrityError:
            return create_error_response(409, "Already exists",
                                         "Product with handle '{}' already exists.".format(
                                             request.json["handle"])
                                         )

        return Response(status=201, headers={
            "Location": api.url_for(EventItem, id=request.json["id"])
        })
        
