import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, User, Account, Transaction
from datetime import date

# ----------------------------
# Setup test database
# ----------------------------
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

# ----------------------------
# Fixtures
# ----------------------------
@pytest.fixture(scope="module")
def test_user():
    db = TestingSessionLocal()
    user = User(email="test@example.com", hashed_password="fakehashedpassword")
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user

@pytest.fixture(scope="module")
def test_account(test_user):
    db = TestingSessionLocal()
    account = Account(user_id=test_user.id, name="Checking", balance=1000.0)
    db.add(account)
    db.commit()
    db.refresh(account)
    db.close()
    return account

@pytest.fixture(scope="module")
def auth_headers(test_user):
    # Here, adjust if you have JWT auth, for simplicity we’ll fake it
    return {"Authorization": f"Bearer {test_user.id}"}

# ----------------------------
# Tests
# ----------------------------
def test_create_transaction(test_account, auth_headers):
    payload = {
        "account_id": test_account.id,
        "amount": 100,
        "type": "income",
        "category": "Salary",
        "date": str(date.today())
    }
    response = client.post("/transactions/", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["amount"] == 100
    assert data["type"] == "income"
    assert data["category"] == "Salary"

def test_get_transactions(auth_headers):
    response = client.get("/transactions/", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_get_transaction(auth_headers):
    response = client.get("/transactions/1", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1

def test_update_transaction(auth_headers):
    payload = {
        "account_id": 1,  # same account
        "amount": 150,
        "type": "income",
        "category": "Bonus",
        "date": str(date.today())
    }
    response = client.put("/transactions/1", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["amount"] == 150
    assert data["category"] == "Bonus"

def test_delete_transaction(auth_headers):
    response = client.delete("/transactions/1", headers=auth_headers)
    assert response.status_code == 204

    # Confirm deletion
    response = client.get("/transactions/1", headers=auth_headers)
    assert response.status_code == 404