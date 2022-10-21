from datetime import datetime, timedelta
from typing import Union

from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Query

from onboarding_app import exceptions
from onboarding_app.config import settings
from onboarding_app.database import Base

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# OAuth2
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def reorder(
    target_model_obj: Base,
    hope_order: int,
    modelList_query_res_by_foreign_key: Query,
):
    if hope_order < 0 or hope_order >= modelList_query_res_by_foreign_key.count():
        raise exceptions.InvalidQueryError

    origin_order = target_model_obj.order_num
    if hope_order > origin_order:
        _reorder_upper_items(
            modelList_query_res_by_foreign_key,
            target_model_obj,
            hope_order,
        )

    elif hope_order < origin_order:
        _reorder_lower_items(
            modelList_query_res_by_foreign_key,
            target_model_obj,
            hope_order,
        )
    target_model_obj.order_num = hope_order


def _reorder_upper_items(
    query_res_filter_by_foreign_key: Query,
    target_model: Base,
    hope_order: int,
):
    query_res_filter_by_foreign_key.filter(
        target_model.__class__.order_num > target_model.order_num,
        target_model.__class__.order_num <= hope_order,
    ).update(
        {target_model.__class__.order_num: target_model.__class__.order_num - 1},
        synchronize_session=False,
    )


def _reorder_lower_items(
    query_res_filter_by_foreign_key: Query,
    target_model: Base,
    hope_order: int,
):
    query_res_filter_by_foreign_key.filter(
        target_model.__class__.order_num < target_model.order_num,
        target_model.__class__.order_num >= hope_order,
    ).update(
        {target_model.__class__.order_num: target_model.__class__.order_num + 1},
        synchronize_session=False,
    )
