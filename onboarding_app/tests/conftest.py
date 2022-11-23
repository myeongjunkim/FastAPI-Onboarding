import pytest
from fastapi.testclient import TestClient

from onboarding_app import schemas
from onboarding_app.database import Base, engine, SessionLocal
from onboarding_app.main import app
from onboarding_app.queries import user as user_query
from onboarding_app.tests.utils import obtain_token_reg


class TestClientWithAuth(TestClient):
    def authenticate(self, username: str):
        token = obtain_token_reg(username)
        self.headers["Authorization"] = f"Bearer {token}"

    def deauthenticate(self):
        self.headers["Authorization"] = None


client = TestClientWithAuth(app)


@pytest.fixture
def db_session():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def clear_db():
    Base.metadata.create_all(bind=engine, checkfirst=True)
    yield
    Base.metadata.drop_all(bind=engine, checkfirst=False)
    engine.dispose()


@pytest.fixture(autouse=True)
def create_dumy_user(db_session):
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

    user_query.create_user(db=db_session, user=admin, is_admin=True)
    user_query.create_user(db=db_session, user=reg1)
    user_query.create_user(db=db_session, user=reg2)
