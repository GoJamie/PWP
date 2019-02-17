import os
import pytest
import tempfile
import time
from datetime import datetime
from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError, StatementError

import app
from app import Location, Sensor, Deployment, Measurement

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# based on http://flask.pocoo.org/docs/1.0/testing/
# we don't need a client for database testing, just the db handle
@pytest.fixture
def db_handle():
    db_fd, db_fname = tempfile.mkstemp()
    app.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_fname
    app.app.config["TESTING"] = True
    
    with app.app.app_context():
        app.db.create_all()
        
    yield app.db
    
    os.close(db_fd)
    os.unlink(db_fname)

def _get_location(sitename="alpha"):
    return Location(
        latitude=63.3,
        longitude=22.6,
        altitude=24.5,
        description="test site {}".format(sitename)
    )

def _get_sensor(number=1):
    return Sensor(
        name="donkeysensor-{}".format(number),
        model="donkeysensor2000",
    )
    
def _get_measurement():
    return Measurement(
        value=44.51,
        time=datetime.now()
    )
    
def _get_deployment():
    return Deployment(
        start=datetime(2019, 1, 1, 0, 0, 1),
        end=datetime(2020, 1, 1, 0, 0, 0),
        name="test deployment"
    )
    
def test_create_instances(db_handle):
    """
    Tests that we can create one instance of each model and save them to the
    database using valid values for all columns. After creation, test that 
    everything can be found from database, and that all relationships have been
    saved correctly.
    """

    # Create everything
    location = _get_location()
    sensor = _get_sensor()
    measurement = _get_measurement()
    deployment = _get_deployment()
    sensor.location = location
    measurement.sensor = sensor
    deployment.sensors.append(sensor)
    db_handle.session.add(location)
    db_handle.session.add(sensor)
    db_handle.session.add(measurement)
    db_handle.session.add(deployment)
    db_handle.session.commit()
    
    # Check that everything exists
    assert Location.query.count() == 1
    assert Sensor.query.count() == 1
    assert Measurement.query.count() == 1
    assert Deployment.query.count() == 1
    db_sensor = Sensor.query.first()
    db_measurement = Measurement.query.first()
    db_location = Location.query.first()
    db_deployment = Deployment.query.first()
    
    # Check all relationships (both sides)
    assert db_measurement.sensor == db_sensor
    assert db_location.sensor == db_sensor
    assert db_sensor.location == db_location
    assert db_sensor in db_deployment.sensors
    assert db_deployment in db_sensor.deployments
    assert db_measurement in db_sensor.measurements    
    
def test_location_sensor_one_to_one(db_handle):
    """
    Tests that the relationship between sensor and location is one-to-one.
    i.e. that we cannot assign the same location for two sensors.
    """
    
    location = _get_location()
    sensor_1 = _get_sensor(1)
    sensor_2 = _get_sensor(2)
    sensor_1.location = location
    sensor_2.location = location
    db_handle.session.add(location)
    db_handle.session.add(sensor_1)
    db_handle.session.add(sensor_2)    
    with pytest.raises(IntegrityError):
        db_handle.session.commit()
        
def test_measurement_ondelete_sensor(db_handle):
    """
    Tests that measurement's sensor foreign key is set to null when the sensor
    is deleted.
    """
    
    measurement = _get_measurement()
    sensor = _get_sensor()
    measurement.sensor = sensor
    db_handle.session.add(measurement)
    db_handle.session.commit()
    db_handle.session.delete(sensor)
    db_handle.session.commit()
    assert measurement.sensor is None
        
def test_location_columns(db_handle):
    """
    Tests the types and restrictions of location columns. Checks that numerical
    values only accepts numbers, and that all of the columns are optional. 
    """
    
    location = _get_location()
    location.latitude = str(location.latitude) + "°"
    db_handle.session.add(location)
    with pytest.raises(StatementError):
        db_handle.session.commit()
        
    db_handle.session.rollback()
        
    location = _get_location()
    location.longitude = str(location.longitude) + "°"
    db_handle.session.add(location)
    with pytest.raises(StatementError):
        db_handle.session.commit()
    
    db_handle.session.rollback()

    location = _get_location()
    location.altitude = str(location.altitude) + "m"
    db_handle.session.add(location)
    with pytest.raises(StatementError):
        db_handle.session.commit()
    
    db_handle.session.rollback()
    
    location = Location()
    db_handle.session.add(location)
    db_handle.session.commit()    
    
def test_sensor_columns(db_handle):
    """
    Tests sensor columns' restrictions. Name must be unique, and name and model
    must be mandatory.
    """

    sensor_1 = _get_sensor()
    sensor_2 = _get_sensor()
    db_handle.session.add(sensor_1)
    db_handle.session.add(sensor_2)    
    with pytest.raises(IntegrityError):
        db_handle.session.commit()

    db_handle.session.rollback()
    
    sensor = _get_sensor()
    sensor.name = None
    db_handle.session.add(sensor)
    with pytest.raises(IntegrityError):
        db_handle.session.commit()
    
    db_handle.session.rollback()
    
    sensor = _get_sensor()
    sensor.model = None
    db_handle.session.add(sensor)
    with pytest.raises(IntegrityError):
        db_handle.session.commit()    
    
def test_measurement_columns(db_handle):
    """
    Tests that a measurement value only accepts floating point values and that
    time only accepts datetime values.
    """
    
    measurement = _get_measurement()
    measurement.value = str(measurement.value) + "kg"
    db_handle.session.add(measurement)
    with pytest.raises(StatementError):
        db_handle.session.commit()
        
    db_handle.session.rollback()
    
    measurement = _get_measurement()
    measurement.time = time.time()
    db_handle.session.add(measurement)
    with pytest.raises(StatementError):
        db_handle.session.commit()
    
def test_deployment_columns(db_handle):
    """
    Tests that all columns in the deployment table are mandatory. Also tests
    that start and end only accept datetime values.
    """
    
    # Tests for nullable
    deployment = _get_deployment()
    deployment.start = None
    db_handle.session.add(deployment)
    with pytest.raises(IntegrityError):
        db_handle.session.commit()
    
    db_handle.session.rollback()

    deployment = _get_deployment()
    deployment.end = None
    db_handle.session.add(deployment)
    with pytest.raises(IntegrityError):
        db_handle.session.commit()
    
    db_handle.session.rollback()

    deployment = _get_deployment()
    deployment.name = None
    db_handle.session.add(deployment)
    with pytest.raises(IntegrityError):
        db_handle.session.commit()
    
    db_handle.session.rollback()
        
    # Tests for column type
    deployment = _get_deployment()
    deployment.start = time.time()
    db_handle.session.add(deployment)
    with pytest.raises(StatementError):
        db_handle.session.commit()
    
    db_handle.session.rollback()
    
    deployment = _get_deployment()
    deployment.end = time.time()
    db_handle.session.add(deployment)
    with pytest.raises(StatementError):
        db_handle.session.commit()
    
