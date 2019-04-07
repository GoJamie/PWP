
from flask import Flask, request, abort, Response, current_app
from .resources.eventitem import EventItem
from .resources.useritem import UserItem
from flask_restful import Api
import json
api = Api(current_app)


class MasonBuilder(dict):
    """
    A convenience class for managing dictionaries that represent Mason
    objects. It provides nice shorthands for inserting some of the more
    elements into the object but mostly is just a parent for the much more
    useful subclass defined next. This class is generic in the sense that it
    does not contain any application specific implementation details.
    """

    def add_error(self, title, details):
        """
        Adds an error element to the object. Should only be used for the root
        object, and only in error scenarios.

        Note: Mason allows more than one string in the @messages property (it's
        in fact an array). However we are being lazy and supporting just one
        message.

        : param str title: Short title for the error
        : param str details: Longer human-readable description
        """

        self["@error"] = {
            "@message": title,
            "@messages": [details],
        }

    def add_namespace(self, ns, uri):
        """
        Adds a namespace element to the object. A namespace defines where our
        link relations are coming from. The URI can be an address where
        developers can find information about our link relations.

        : param str ns: the namespace prefix
        : param str uri: the identifier URI of the namespace
        """

        if "@namespaces" not in self:
            self["@namespaces"] = {}

        self["@namespaces"][ns] = {
            "name": uri
        }

    def add_control(self, ctrl_name, href, **kwargs):
        """
        Adds a control property to an object. Also adds the @controls property
        if it doesn't exist on the object yet. Technically only certain
        properties are allowed for kwargs but again we're being lazy and don't
        perform any checking.

        The allowed properties can be found from here
        https://github.com/JornWildt/Mason/blob/master/Documentation/Mason-draft-2.md

        : param str ctrl_name: name of the control (including namespace if any)
        : param str href: target URI for the control
        """

        if "@controls" not in self:
            self["@controls"] = {}

        self["@controls"][ctrl_name] = kwargs
        self["@controls"][ctrl_name]["href"] = href


LINK_RELATIONS_URL = "/eventhub/link-relations/"
USER_PROFILE = "/profiles/user/"
ERROR_PROFILE = "/profiles/error/"
MASON = "application/vnd.mason+json"

EVENT_PROFILE = "/profiles/EVENT/"
ERROR_PROFILE = "/profiles/error/"


def create__user_error_response(status_code, title, message=None):
    resource_url = request.path
    body = MasonBuilder(resource_url=resource_url)
    body.add_error(title, message)
    body.add_control("profile", href=ERROR_PROFILE)
    return Response(json.dumps(body), status_code, mimetype=MASON)


def create_event_error_response(status_code, title, message=None):
    resource_url = request.path
    body = MasonBuilder(resource_url=resource_url)
    body.add_error(title, message)
    body.add_control("profile", href=ERROR_PROFILE)
    return Response(json.dumps(body), status_code, mimetype=MASON)


class InventoryBuilder(MasonBuilder):

    @staticmethod
    def event_schema():
        schema = {
            "type": "object",
            "required": ["name", "description"]
        }
        props = schema["properties"] = {}
        props["id"] = {
            "description": "Events's unique name",
            "type": "number"
        }
        props["name"] = {
            "description": "name of the event's model",
            "type": "string"
        }

        props["description"] = {
            "description": "description of the event's model",
            "type": "number"
        },
        props["place"] = {
            "description": "place of the event's model",
            "type": "string"
        }

        props["time"] = {
            "description": "time of the event's model",
            "type": "DateTime"
        }

        return schema

    @staticmethod
    def user_schema():
        schema = {
            "type": "object",
            "required": ["name"]
        }
        props = schema["properties"] = {}
        props["id"] = {
            "description": "Users's unique id",
            "type": "number"
        }
        props["name"] = {
            "description": "name of the user",
            "type": "string"
        }

        props["place"] = {
            "description": "place of the user",
            "type": "string"
        }
        props["picure"] = {
            "description": "picture of the user",
            "type": "string"
        }
        return schema

    def add_control_delete_event(self, id):
        self.add_control(
            "eventhub:delete",
            href=api.url_for(EventItem, id=id),
            method="DELETE",
            title="Delete this event"
        )

    def add_control_all_events(self):
        self.add_control(
            "eventshub:events-all",
            "/api/events/",
            method="GET",
            title="get all events"
        )

    def add_control_add_event(self):

        self.add_control(
            "eventhub:add-event",
            "/api/events/",
            method="POST",
            encoding="json",
            title="Add a new product",
            schema=self.event_schema()
        )

    def add_control_edit_event(self, id):

        self.add_control(
            "edit",
            href=api.url_for(EventItem, id=id),
            method="Put",
            encoding="json",
            title="Edit a product",
            schema=self.event_schema()
        )

    def add_control_delete_user(self, id):
        self.add_control(
            "userhub:delete",
            href=api.url_for(UserItem, id=id),
            method="DELETE",
            title="Delete this resource"
        )

    def add_control_all_users(self):
        self.add_control(
            "usershub:events-all",
            "/api/users/",
            method="GET",
            title="get all users"
        )

    def add_control_add_user(self):

        self.add_control(
            "userhub:add-event",
            "/api/users/",
            method="POST",
            encoding="json",
            title="Add a new product",
            schema=self.event_schema()
        )

    def add_control_edit_user(self, id):

        self.add_control(
            "edit",
            href=api.url_for(UserItem, id=id),
            method="Put",
            encoding="json",
            title="Edit a product",
            schema=self.event_schema()
        )
