from flask_restful import Resource

from flask import Flask, request, abort, Response, current_app
from resources.eventitem import EventItem
from models import Event
from utils import InventoryBuilder, MasonBuilder

api = Api(current_app)


LINK_RELATIONS_URL = "/eventhub/link-relations/"
USER_PROFILE = "/profiles/user/"
ERROR_PROFILE = "/profiles/error/"
MASON = "application/vnd.mason+json"

EVENT_PROFILE = "/profiles/EVENT/"
ERROR_PROFILE = "/profiles/error/"


class EventCollection(Resource):

    def get(self, handle):
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
        except (KeyError, ValueError, IntegrityError):
            abort(400)

    def put(self, handle):


api.add_resource(ProductCollection, "/api/events/")
