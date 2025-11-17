import pytest
from fastapi.testclient import TestClient
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker

from src.main import app
from src.models.database import Base, User
from src.dependencies import get_db
from src.config import settings

# SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Create password context for tests
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="module")
def clear_users():
    with next(override_get_db()) as db:
        db.query(User).delete()
        db.commit()


@pytest.fixture(scope="module")
def test_user(clear_users):
    hashed_password = pwd_context.hash("testpassword")

    with next(override_get_db()) as db:
        user = User(username="testuser", hashed_password=hashed_password)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user


@pytest.fixture(scope="module")
def test_token(test_user):
    access_token = jwt.encode({"sub": test_user.username}, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return access_token


def test_register_user():
    response = client.post("/api/v1/users/register", json={
        "username": "newuser",
        "password": "NewPassword123!"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "newuser"


def test_login_for_access_token(test_user):
    response = client.post("/api/v1/users/login", data={
        "username": "testuser",
        "password": "testpassword"
    })

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_read_users_me(test_token):
    headers = {"Authorization": f"Bearer {test_token}"}
    response = client.get("/api/v1/users/me", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"