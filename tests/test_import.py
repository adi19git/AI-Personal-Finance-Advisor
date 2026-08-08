import pytest
import io
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.models.transaction import Transaction
from app.models.user import User

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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

def get_auth_token():
    # Register
    client.post(
        "/api/auth/register",
        json={"email": "import_user@example.com", "username": "import_user", "password": "password", "full_name": "Import User"},
    )
    # Login
    res = client.post(
        "/api/auth/login",
        data={"username": "import_user", "password": "password"},
    )
    return res.json()["access_token"]

def test_import_valid_csv():
    token = get_auth_token()
    
    csv_content = """Date,Description,Amount,Transaction Type
2026-08-01,Groceries,45.50,debit
2026-08-02,Salary,2000.00,credit
"""
    file_obj = io.BytesIO(csv_content.encode('utf-8'))

    response = client.post(
        "/api/import/",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("test.csv", file_obj, "text/csv")}
    )
    
    assert response.status_code == 200
    assert response.json()["count"] == 2

    # Verify DB
    db = TestingSessionLocal()
    txs = db.query(Transaction).all()
    assert len(txs) == 2
    assert txs[0].amount == 45.5
    assert txs[0].transaction_type == "debit"
    assert txs[1].amount == 2000.0
    assert txs[1].transaction_type == "credit"
    db.close()

def test_import_missing_columns():
    token = get_auth_token()
    
    csv_content = """Something,Random
2026-08-01,Hello
"""
    file_obj = io.BytesIO(csv_content.encode('utf-8'))

    response = client.post(
        "/api/import/",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("bad.csv", file_obj, "text/csv")}
    )
    
    assert response.status_code == 400
    assert "Could not find a valid 'Date' column" in response.json()["detail"]
