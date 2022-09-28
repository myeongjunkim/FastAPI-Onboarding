from datetime import timedelta

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from onboarding_app import database, dependencies, schemas, utils
from onboarding_app.config import settings
from onboarding_app.queries import user as user_query

user_router = APIRouter()


@user_router.post("/users/signup", response_model=schemas.UserResponse)
def signup(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    res = user_query.create_user(db=db, user=user)
    return jsonable_encoder(res)


@user_router.get("/users", response_model=list[schemas.User])
def fetch_users(
    offset: int = 0, limit: int = 100, db: Session = Depends(database.get_db)
):
    return user_query.get_users(db, offset=offset, limit=limit)


# OAuth2
@user_router.post("/users/token", response_model=schemas.Token)
async def get_token(
    db: Session = Depends(database.get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    user = user_query.authenticate_user(
        db=db, username=form_data.username, password=form_data.password
    )
    access_token_expires = timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_SECONDS)
    access_token = utils.create_access_token(
        data={"username": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@user_router.get("/users/me/", response_model=schemas.User)
async def read_users_me(
    current_user: schemas.User = Depends(dependencies.get_current_user),
):
    return current_user


@user_router.get("/users/{user_id}", response_model=schemas.User)
def get_user(user_id: int, db: Session = Depends(database.get_db)):
    return user_query.get_user(db, user_id=user_id)
