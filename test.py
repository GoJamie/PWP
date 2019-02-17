import os
import pytest
import tempfile
import time
from datetime import datetime
from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError, StatementError

import database
from database import Event, User, LoginUser

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

@pytest.fixture
def db_handle():
    db_fd, db_fname = tempfile.mkstemp()
    database.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_fname
    database.app.config["TESTING"] = True
    
    with database.app.app_context():
        database.db.create_all()
        
    yield database.db
    
    os.close(db_fd)
    os.unlink(db_fname)

def _get_event(sitename="alpha"):
    return Event(
        name='PWP Meeting',
        history=False,
        description="test site {}".format(sitename),
    )

def _get_user():
    return User(
        name='Bangju Wang',
    )
    
def _get_loginuser():
    user = LoginUser(username='user-1')
    user.hash_password('password')
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