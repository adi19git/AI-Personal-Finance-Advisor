import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


def test_register_user():
    response = client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "username": "testuser", "password": "testpassword", "full_name": "Test User"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data


def test_login_user():
    # Register first
    client.post(
        "/api/auth/register",
        json={"email": "test2@example.com", "username": "testuser2", "password": "testpassword2", "full_name": "Test User 2"},
    )

    # Login
    response = client.post(
        "/api/auth/login",
        data={"username": "testuser2", "password": "testpassword2"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_get_me():
    # Register
    client.post(
        "/api/auth/register",
        json={"email": "test3@example.com", "username": "testuser3", "password": "testpassword3", "full_name": "Test User 3"},
    )

    # Login
    login_res = client.post(
        "/api/auth/login",
        data={"username": "testuser3", "password": "testpassword3"},
    )
    token = login_res.json()["access_token"]

    # Get Me
    me_res = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "test3@example.com"


def test_unauthorized_access():
    me_res = client.get("/api/auth/me")
    assert me_res.status_code == 401
