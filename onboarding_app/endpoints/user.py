from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from onboarding_app import database, schemas
from onboarding_app.queries import user as user_query
from onboarding_app.queries.user import UserDuplicatedError

user_router = APIRouter()


@user_router.post("/users/signup", response_model=schemas.UserResponse)
def signup(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    try:
        res = user_query.create_user(db=db, user=user)
        return jsonable_encoder(res)
    except UserDuplicatedError:
        raise HTTPException(status_code=400, detail="User info is duplicated")


@user_router.get("/users", response_model=list[schemas.User])
def fetch_users(
    offset: int = 0, limit: int = 100, db: Session = Depends(database.get_db)
):
    users = user_query.get_users(db, offset=offset, limit=limit)
    return users


@user_router.get("/users/{user_id}", response_model=schemas.User)
def get_user(user_id: int, db: Session = Depends(database.get_db)):
    db_user = user_query.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
