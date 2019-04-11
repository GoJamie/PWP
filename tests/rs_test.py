import json
import os
import pytest
import tempfile
from jsonschema import validate
from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError, StatementError

import sys
import os

o_path = os.getcwd()
sys.path.append(o_path)

from Eventhub import app, db
from Eventhub.models import Event, User, LoginUser

@pytest.fixture
def client():
    db_fd, db_fname = tempfile.mkstemp()
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_fname
    app.config["TESTING"] = True

    db.create_all()
    _populate_db()

    yield app.test_client()

    db.session.remove()
    os.close(db_fd)
    os.unlink(db_fname)

def _populate_db():
    """
    Pre-populate database with 1 event, 3 users and 3 loginusers.
    """
    event = Event(
        name='PWP Meeting',
        creator_id = 1,
        description="Test event"   
    )
    for i in range(1, 2):
        user = User(name='user-{}'.format(i))
        login_user = LoginUser(username='user-{}'.format(i))
        login_user.hash_password('password')
        login_user.user = user
        db.session.add(user)
        db.session.add(login_user)
        event.joined_users.append(user)

    user = User(name='user-{}'.format(3))
    login_user = LoginUser(username='user-{}'.format(3))
    login_user.hash_password('password')
    login_user.user = user
    db.session.add(user)
    db.session.add(login_user)
    event.creator = user
    event.joined_users.append(user)

    db.session.add(event)

    db.session.commit()

def _check_namespace(client, response):
    """
    Check the "eventhub" namespace.
    """
    ns_href = response["@namespaces"]["eventhub"]["name"]
    resp = client.get(ns_href)
    assert resp.status_code == 200

def _check_control_get_method(ctrl, client, obj):

    href = obj["@controls"][ctrl]["href"]
    resp = client.get(href)
    assert resp.status_code == 200

def _check_control_delete_method(ctrl, client, obj):

    href = obj["@controls"][ctrl]["href"]
    method = obj["@controls"][ctrl]["method"].lower()
    assert method == "delete"
    resp = client.delete(href)
    assert resp.status_code == 204

def _get_event_json(number=1):
    return {
                "name":"event-{}".format(number),
                "description": "test",
                "place": "ousadalu",
                "time":"28012119",
                "creatorId": 1
            }

def _get_user_json(number=1):
    return {
                "username":"user-{}".format(number),
                "name": "test user",
                "password":"password"
            }

def _check_control_put_method(ctrl, client, obj, putType):
    """
    Checks a PUT type control from a JSON object be it root document or an item
    in a collection. In addition to checking the "href" attribute, also checks
    that method, encoding and schema can be found from the control. Also
    validates a valid sensor against the schema of the control to ensure that
    they match. Finally checks that using the control results in the correct
    status code of 204.
    """
    
    ctrl_obj = obj["@controls"][ctrl]
    href = ctrl_obj["href"]
    method = ctrl_obj["method"].lower()
    schema = ctrl_obj["schema"]
    assert method == "put"
    print(href)
    if putType == "event":
        body = _get_event_json()
    elif putType == "user":
        body = _get_user_json()
    validate(body, schema)
    resp = client.put(href, json=body)
    assert resp.status_code == 204

def _check_control_post_method(ctrl, client, obj):
    ctrl_obj = obj["@controls"][ctrl]
    href = ctrl_obj["href"]
    method = ctrl_obj["method"].lower()
    schema = ctrl_obj["schema"]
    assert method == "post"
    if ctrl.endswith("event"):
        body = _get_event_json()
    elif ctrl.endswith("user"):
        body = _get_user_json()
    validate(body, schema)
    resp = client.post(href, json=body)
    assert resp.status_code == 201

class TestEventCollection(object):
    """
    This class implements tests for each HTTP method in questionnaire collection
    resource. 
    """
    RESOURCE_URL = "/api/events/"

    def test_get(self,client):
        """
        Tests the GET method. Checks that the response status code is 200, and
        then checks that all of the expected attributes and controls are
        present, and the controls work. Also checks that all of the items from
        the DB popluation are present, and their controls.
        """
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        _check_namespace(client, body)
        #_check_control_post_method("eventhub:add-event", client, body)
        assert len(body["items"]) == 1
        for item in body["items"]:
            #_check_control_get_method("self", client, item)
            #_check_control_get_method("profile", client, item)
            assert "id" in item
            assert "name" in item
            assert "description" in item 

    def test_post(self, client):
        """
        Tests the POST method. Checks all of the possible error codes, and 
        also checks that a valid request receives a 201 response with a 
        location header that leads into the newly created resource.
        """
        valid = _get_event_json(number=2)

        # test with valid and see that it exists afterward
        resp = client.post(self.RESOURCE_URL, data=valid)
        body = json.loads(client.get(self.RESOURCE_URL).data)
        id = body["items"][-1]["id"]
        assert resp.status_code == 201
        assert resp.headers["Location"].endswith(self.RESOURCE_URL + str(id) + "/")
        resp = client.get(resp.headers["Location"])
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["name"] == "event-2"
        assert body["description"] == "test"

        # test with wrong content type(must be json)
        resp = client.post(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

        # remove title field for 400
        valid.pop("name")
        resp = client.post(self.RESOURCE_URL, data=valid)
        assert resp.status_code == 400

class TestEventItem(object):
    RESOURCE_URL = "/api/events/1/"
    INVALID_URL = "/api/events/-1/"

    def test_get(self,client):
        """
        Tests the GET method. Checks that the response status code is 200, and
        then checks that all of the expected attributes and controls are
        present, and the controls work. Also checks that all of the items from
        the DB popluation are present, and their controls.
        """
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["name"] == "event-1"
        assert body["description"] == "test"
        _check_namespace(client, body)
        _check_control_get_method("profile", client, body)
        _check_control_get_method("eventshub:events-all", client, body)
        _check_control_put_method("edit", client, body,"event")
        _check_control_delete_method("eventhub:delete", client, body)
        resp = client.get(self.INVALID_URL)
        assert resp.status_code == 404
            
    def test_put(self,client):
        """Test for valid PUT method"""
        valid = _get_event_json(number=3)

        # test with valid
        resp = client.put(self.RESOURCE_URL,data=valid)
        assert resp.status_code == 204

        # test with another url
        resp = client.put(self.INVALID_URL, data=valid)
        assert resp.status_code == 404

        # test with wrong content type
        resp = client.put(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

        # remove field title for 400
        valid.pop("name")
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 405

        valid = _get_event_json(number=4)
        resp = client.put(self.RESOURCE_URL, json=valid)
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["name"] == valid["name"] and body["description"] == valid["description"]

class TestEventsbyUser(object):
    RESOURCE_URL = "/api/users/1/events/"
    INVALID_URL = "/api/users/-1/events/"

    def test_get(self,client):
        """Tests for questions by questionnaire GET method."""
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["username"] == "user-1"
        assert body["name"] == "test user"
        _check_namespace(client, body)
        _check_control_get_method("self", client, body)
        _check_control_get_method("profile", client, body)
        _check_control_get_method("eventhub:users-all", client, body)
        _check_control_put_method("edit", client, body,"user")
        _check_control_delete_method("eventhub:delete", client, body)
        resp = client.get(self.INVALID_URL)
        assert resp.status_code == 404
 
        assert resp.status_code == 200
        body = json.loads(resp.data)
        _check_namespace(client, body)
        for item in body["items"]:
            assert item["name"] == "event-1"
            assert item["description"] == "test"
            _check_namespace(client, item)
            _check_control_get_method("profile", client, item)
            _check_control_get_method("eventshub:events-all", client, item)
            _check_control_put_method("edit", client, item,"event")
            _check_control_delete_method("eventhub:delete", client, item)
 
class TestJoinEvent(object):
    RESOURCE_URL = "/api/users/1/events/1/"
    INVALID_URL = "/api/users/1/events/-1/"

    def test_put(self,client):
        """Test for valid PUT method"""
        valid = {"random":"random"}

        # test with valid
        resp = client.put(self.RESOURCE_URL,data=valid)
        assert resp.status_code == 204

        # test with another url
        resp = client.put(self.INVALID_URL, data=valid)
        assert resp.status_code == 404

        # test with wrong content type
        resp = client.put(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

        # remove field title for 400
        resp = client.put(self.RESOURCE_URL,json=valid)
        assert resp.status_code == 405

        valid = {
	    "username":"user-{}".format(4),
        "name": "user",
        "password":"password"
        }
        resp = client.put(self.RESOURCE_URL, json=valid)
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["name"] == valid["name"] and body["username"] == valid["username"]

    def test_delete(self, client):

        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 204
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 404
        resp = client.delete(self.INVALID_URL)
        assert resp.status_code == 404

class TestUserCollection(object):
    """
    This class implements tests for each HTTP method in questionnaire collection
    resource. 
    """
    RESOURCE_URL = "/api/events/"

    def test_get(self,client):
        """
        Tests the GET method. Checks that the response status code is 200, and
        then checks that all of the expected attributes and controls are
        present, and the controls work. Also checks that all of the items from
        the DB popluation are present, and their controls.
        """
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        _check_namespace(client, body)
        #_check_control_post_method("eventhub:add-user", client, body)
        #_check_control_post_method("eventhub:all-user", client, body)        
        assert len(body["items"]) == 1
        for item in body["items"]:
            #_check_control_get_method("self", client, item)
            #_check_control_get_method("profile", client, item)
            assert "name" in item

    def test_post(self, client):
        """
        Tests the POST method. Checks all of the possible error codes, and 
        also checks that a valid request receives a 201 response with a 
        location header that leads into the newly created resource.
        """
        valid = _get_user_json(number=2)

        # test with valid and see that it exists afterward
        resp = client.post(self.RESOURCE_URL, data=valid)
        body = json.loads(client.get(self.RESOURCE_URL).data)
        id = body["items"][-1]["id"]
        assert resp.status_code == 201
        assert resp.headers["Location"].endswith(self.RESOURCE_URL + str(id) + "/")
        resp = client.get(resp.headers["Location"])
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["username"] == "user-2"
        assert body["name"] == "test user"
        assert body["password"] == "password"

        # test with wrong content type(must be json)
        resp = client.post(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

        # remove title field for 400
        valid.pop("name")
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400

class TestUserItem(object):
    RESOURCE_URL = "/api/users/1/"
    INVALID_URL = "/api/users/-1/"

    def test_get(self,client):
        """
        Tests the GET method. Checks that the response status code is 200, and
        then checks that all of the expected attributes and controls are
        present, and the controls work. Also checks that all of the items from
        the DB popluation are present, and their controls.
        """
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["username"] == "user-1"
        assert body["name"] == "test user"
        _check_namespace(client, body)
        _check_control_get_method("self", client, body)
        _check_control_get_method("profile", client, body)
        _check_control_get_method("eventhub:users-all", client, body)
        _check_control_put_method("edit", client, body,"user")
        _check_control_delete_method("eventhub:delete", client, body)
        resp = client.get(self.INVALID_URL)
        assert resp.status_code == 404
            
    def test_put(self,client):
        """Test for valid PUT method"""
        valid = _get_user_json(number=3)

        # test with valid
        resp = client.put(self.RESOURCE_URL,data=valid)
        assert resp.status_code == 204

        # test with another url
        resp = client.put(self.INVALID_URL, data=valid)
        assert resp.status_code == 404

        # test with wrong content type
        resp = client.put(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

        # remove field title for 400
        valid.pop("name")
        resp = client.post(self.RESOURCE_URL, data=valid)
        assert resp.status_code == 405

        valid = {
	    "username":"user-{}".format(4),
        "name": "user",
        "password":"password"
        }
        resp = client.put(self.RESOURCE_URL, json=valid)
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["name"] == valid["name"] and body["username"] == valid["username"]

    def test_delete(self, client):

        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 204
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 404
        resp = client.delete(self.INVALID_URL)
        assert resp.status_code == 404