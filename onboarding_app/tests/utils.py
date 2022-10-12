from datetime import timedelta

from onboarding_app import utils
from onboarding_app.config import settings


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
