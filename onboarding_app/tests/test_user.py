from datetime import timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from onboarding_app import schemas, utils
from onboarding_app.config import settings
from onboarding_app.database import Base, get_db
from onboarding_app.main import app
from onboarding_app.queries import user as user_query

TEST_DATABASE_URL = "sqlite:///./onboarding_app/tests/fake.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
Base.metadata.create_all(bind=engine)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def fake_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = fake_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_db():
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(autouse=True)
def create_dumy_user():
    admin = schemas.UserCreate(
        username="admin",
        email="admin@example.com",
        password1="admin",
        password2="admin",
    )

    reg1 = schemas.UserCreate(
        username="reg1",
        email="reg1@example.com",
        password1="reg1",
        password2="reg1",
    )

    user_query.create_user(db=TestingSessionLocal(), user=admin, is_admin=True)
    user_query.create_user(db=TestingSessionLocal(), user=reg1)


def obtain_token_admin():
    access_token_expires = timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_SECONDS)
    access_token = utils.create_access_token(
        data={"username": "admin"}, expires_delta=access_token_expires
    )
    return access_token


def obtain_token_reg1():
    access_token_expires = timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_SECONDS)
    access_token = utils.create_access_token(
        data={"username": "reg1"}, expires_delta=access_token_expires
    )
    return access_token


def test_signup_success():
    # When
    signup_response = client.post(
        "/users/signup",
        json={
            "username": "reg2",
            "email": "reg2@example.com",
            "password1": "reg2",
            "password2": "reg2",
        },
    )

    # Then
    assert signup_response.status_code == 200
    assert signup_response.json()["username"] == "reg2"


def test_login_success():
    # When
    response_token = client.post(
        "/users/token",
        data={
            "username": "admin",
            "password": "admin",
        },
        headers={"content-type": "application/x-www-form-urlencoded"},
    )

    # Then
    assert response_token.status_code == 200
    assert response_token.json() is not None


def test_only_admin_can_fetch_users():
    # Given
    admin_token = obtain_token_admin()
    user_token = obtain_token_reg1()

    # When
    response_users_by_admin = client.get(
        "/users",
        headers={"Authorization": "Bearer " + admin_token},
    )
    response_users_by_reg1 = client.get(
        "/users",
        headers={"Authorization": "Bearer " + user_token},
    )

    # Then
    assert response_users_by_admin.status_code == 200
    assert len(response_users_by_admin.json()) == 2
    assert response_users_by_reg1.status_code == 401


def test_only_admin_can_get_user():
    # Given
    admin_token = obtain_token_admin()
    user_token = obtain_token_reg1()
    check_user = user_query.get_user_by_username(
        db=TestingSessionLocal(), username="reg1"
    )

    # When
    response_by_admin = client.get(
        "/users/" + str(check_user.id),
        headers={"Authorization": "Bearer " + admin_token},
    )
    response_by_reg1 = client.get(
        "/users/" + str(check_user.id),
        headers={"Authorization": "Bearer " + user_token},
    )

    # Then
    assert response_by_admin.status_code == 200
    assert response_by_admin.json()["username"] == "reg1"
    assert response_by_reg1.status_code == 401
