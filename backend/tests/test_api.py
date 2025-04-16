import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from main import app

# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the get_db dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create test client
client = TestClient(app)

@pytest.fixture(scope="function")
def test_db():
    # Create the database tables
    Base.metadata.create_all(bind=engine)
    yield
    # Drop the database tables
    Base.metadata.drop_all(bind=engine)

def test_read_main(test_db):
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert "Welcome to the EGG Monitor API" in response.json()["message"]

def test_create_user(test_db):
    """Test creating a user"""
    response = client.post(
        "/api/users/",
        json={"user_name": "test_user", "user_age": 30},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["user_name"] == "test_user"
    assert data["user_age"] == 30
    assert "id" in data

def test_read_users(test_db):
    """Test reading users"""
    # Create a test user first
    client.post(
        "/api/users/",
        json={"user_name": "test_user", "user_age": 30},
    )
    
    response = client.get("/api/users/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["user_name"] == "test_user"

def test_create_sensor(test_db):
    """Test creating a sensor"""
    response = client.post(
        "/api/sensors/",
        json={"sensor_name": "test_sensor", "sensor_data_rate": 100.0},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["sensor_name"] == "test_sensor"
    assert data["sensor_data_rate"] == 100.0
    assert "id" in data

def test_read_sensors(test_db):
    """Test reading sensors"""
    # Create a test sensor first
    client.post(
        "/api/sensors/",
        json={"sensor_name": "test_sensor", "sensor_data_rate": 100.0},
    )
    
    response = client.get("/api/sensors/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["sensor_name"] == "test_sensor"

def test_assign_sensor_to_user(test_db):
    """Test assigning a sensor to a user"""
    # Create a test user
    user_response = client.post(
        "/api/users/",
        json={"user_name": "test_user", "user_age": 30},
    )
    user_id = user_response.json()["id"]
    
    # Create a test sensor
    sensor_response = client.post(
        "/api/sensors/",
        json={"sensor_name": "test_sensor", "sensor_data_rate": 100.0},
    )
    sensor_id = sensor_response.json()["id"]
    
    # Assign sensor to user
    response = client.post(f"/api/users/{user_id}/sensors/{sensor_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert len(data["sensors"]) > 0
    assert data["sensors"][0]["id"] == sensor_id
