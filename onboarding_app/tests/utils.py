from datetime import timedelta

from sqlalchemy.orm import Session

from onboarding_app import exceptions, models, schemas, utils
from onboarding_app.config import settings


def obtain_token_admin():
    access_token_expires = timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_SECONDS)
    access_token = utils.create_access_token(
        data={"username": "admin"}, expires_delta=access_token_expires
    )
    return access_token


def obtain_token_reg(username: str):
    access_token_expires = timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_SECONDS)
    access_token = utils.create_access_token(
        data={"username": username}, expires_delta=access_token_expires
    )
    return access_token


def get_wishlist_by_name(
    db: Session, name: str, current_user: schemas.User
) -> models.Wishlist:
    db_wishlist = db.query(models.Wishlist).filter(
        models.Wishlist.user_id == current_user.id, models.Wishlist.name == name
    )
    if not db_wishlist.first():
        raise exceptions.DataDoesNotExistError
    return db_wishlist.first()
