from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from onboarding_app import database, exceptions, models
from onboarding_app.config import settings
from onboarding_app.queries import user as user_query

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token")


async def get_current_user(
    db: Session = Depends(database.get_db), token: str = Depends(oauth2_scheme)
) -> models.User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
    except JWTError:
        raise exceptions.CredentialsError

    user = user_query.get_user_by_username(db, payload.get("username"))
    if not user.is_active:
        raise exceptions.InactiveUserError
    return user


async def is_admin(
    db: Session = Depends(database.get_db), token: str = Depends(oauth2_scheme)
) -> bool:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
    except JWTError:
        raise exceptions.CredentialsError

    user = user_query.get_user_by_username(db, payload.get("username"))
    if not user.is_admin:
        raise exceptions.PermissionDeniedError("관리자만 요청할 수 있습니다.")
    return True
