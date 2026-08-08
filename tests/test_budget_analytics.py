import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.models.category import Category
from app.models.transaction import Transaction

SQLALCHEMY_DATABASE_URL = "sqlite:///./test2.db"
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
    client.post(
        "/api/auth/register",
        json={"email": "metrics@example.com", "username": "metrics", "password": "password", "full_name": "Metrics User"},
    )
    res = client.post(
        "/api/auth/login",
        data={"username": "metrics", "password": "password"},
    )
    return res.json()["access_token"]

def test_budget_and_analytics():
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Upload a CSV to create categories and transactions
    csv_content = """Date,Description,Amount,Transaction Type
2026-08-01,Food,50.00,debit
2026-08-02,Food,20.00,debit
"""
    import io
    file_obj = io.BytesIO(csv_content.encode('utf-8'))
    import_res = client.post(
        "/api/import/",
        headers=headers,
        files={"file": ("test.csv", file_obj, "text/csv")}
    )
    assert import_res.status_code == 200

    # Get the automatically created category ID from the transaction
    db = TestingSessionLocal()
    from app.models.transaction import Transaction
    tx = db.query(Transaction).filter(Transaction.description == "Food").first()
    cat_food_id = tx.category_id
    cat_name = tx.category.name
    db.close()
    
    # 2. Test Budget Creation
    res_budget = client.post(
        "/api/budgets/",
        headers=headers,
        json={
            "category_id": cat_food_id,
            "monthly_limit": 100.0,
            "period": "2026-08"
        }
    )
    assert res_budget.status_code == 201
    b_data = res_budget.json()
    assert b_data["spent"] == 70.0
    assert b_data["remaining"] == 30.0
    assert b_data["usage_percent"] == 70.0
    assert b_data["is_over_budget"] == False
    
    # 3. Test Analytics Dashboard
    res_dash = client.get(
        "/api/analytics/dashboard",
        headers=headers
    )
    assert res_dash.status_code == 200
    d_data = res_dash.json()
    assert d_data["total_expenses"] == 70.0
    assert len(d_data["top_categories"]) == 1
    assert d_data["top_categories"][0]["category_name"] == cat_name
    assert len(d_data["recent_anomalies"]) >= 0
