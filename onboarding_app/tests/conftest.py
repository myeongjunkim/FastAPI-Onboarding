import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from onboarding_app import schemas
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

    reg2 = schemas.UserCreate(
        username="reg2",
        email="reg2@example.com",
        password1="reg2",
        password2="reg2",
    )

    user_query.create_user(db=TestingSessionLocal(), user=admin, is_admin=True)
    user_query.create_user(db=TestingSessionLocal(), user=reg1)
    user_query.create_user(db=TestingSessionLocal(), user=reg2)
