import os
import pytest
import tempfile
import time
from datetime import datetime
from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError, StatementError

import sys
import os

o_path = os.getcwd()
sys.path.append(o_path)

from Eventhub import app, db
from Eventhub.models import Event, User, LoginUser

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

@pytest.fixture
def db_handle():
    db_fd, db_fname = tempfile.mkstemp()
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_fname
    app.config["TESTING"] = True
    
    with app.app_context():
        db.create_all()
        
    yield db
    

def _get_event():
    return Event(
        id='1',
        name='PWP Meeting',
        description="Test event"
    )

def _get_user():
    return User(
        name='Bangju Wang1',
        id = 1
    )
    
def _get_loginuser(number=1):
    user = LoginUser(username='user-{}'.format(number))
    return user

def test_create_instances(db_handle):
    """
    Tests that we can create one instance of each model and save them to the
    database using valid values for all columns. After creation, test that 
    everything can be found from database, and that all relationships have been
    saved correctly.
    """

    # Create everything
    event = _get_event()
    user = _get_user()
    loginuser = _get_loginuser()
    
    loginuser.password_hash = loginuser.generate_hash('password')
    loginuser.user = user
    event.creator = user
    event.joined_users.append(user)

    db_handle.session.add(user)
    db_handle.session.add(loginuser)
    db_handle.session.add(event)
    db_handle.session.commit()
    
    # Check that everything exists
    assert Event.query.count() == 1
    assert User.query.count() == 1
    assert LoginUser.query.count() == 1
    db_event = Event.query.first()
    db_user = User.query.first()
    db_loginuser = LoginUser.query.first()
    
    # Check all relationships (both sides)
    assert db_event.creator == db_user
    assert db_loginuser.user == db_user
    assert db_user in db_event.joined_users
    assert db_event in db_user.joined_events

def test_user_loginuser_one_to_one(db_handle):
    """
    Tests that the relationship between user and loginuser is one-to-one.
    i.e. that we cannot assign the same user for two loginusers.
    """
    
    user = _get_user()
    loginuser_1 = _get_loginuser(1)
    loginuser_2 = _get_loginuser(2)
    loginuser_1.user = user
    loginuser_2.user = user
    db_handle.session.add(user)
    db_handle.session.add(loginuser_1)
    db_handle.session.add(loginuser_2)    
    with pytest.raises(IntegrityError):
        db_handle.session.commit()

def test_event_ondelete_creator(db_handle):
    """
    Tests that Event's creator foreign key is set to null when the creator
    is deleted.
    """
    
    user = _get_user()
    event = _get_event()
    event.creator = user
    db_handle.session.add(event)
    db_handle.session.commit()
    db_handle.session.delete(user)
    db_handle.session.commit()
    assert event.creator is None

def test_event_columns(db_handle):
    """
    Tests the types and restrictions of event columns. Checks that name must be unique, 
    and name, description and history must be mandatory. 
    """
    
    event_1 = _get_event()
    event_2 = _get_event()
    db_handle.session.add(event_1)
    db_handle.session.add(event_2)    
    with pytest.raises(IntegrityError):
        db_handle.session.commit()

    db_handle.session.rollback()
    
    event = _get_event()
    event.name = None
    db_handle.session.add(event)
    with pytest.raises(IntegrityError):
        db_handle.session.commit()
    
    db_handle.session.rollback()
    
    event = _get_event()
    event.description = None
    db_handle.session.add(event)
    with pytest.raises(IntegrityError):
        db_handle.session.commit()
        
    db_handle.session.rollback()

def test_user_columns(db_handle):
    """
    Tests the types and restrictions of user columns. Checks that name must be unique and mandatory. 
    """
    
    user_1 = _get_user()
    user_2 = _get_user()
    db_handle.session.add(user_1)
    db_handle.session.add(user_2)    
    with pytest.raises(IntegrityError):
         db_handle.session.commit()

    db_handle.session.rollback()
    
    user = _get_user()
    user.name = None
    db_handle.session.add(user)
    with pytest.raises(IntegrityError):
        db_handle.session.commit()
