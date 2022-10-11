from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from onboarding_app import exceptions, models, schemas, utils


def get_user(db: Session, user_id: int) -> models.User:
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise exceptions.DataDoesNotExistError
    return user


def get_user_by_username(db: Session, username: str) -> models.User:
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise exceptions.DataDoesNotExistError
    return user


def get_users(db: Session, offset: int = 0, limit: int = 100) -> list[models.User]:
    return db.query(models.User).offset(offset).limit(limit).all()


def create_user(
    db: Session, user: schemas.UserCreate, is_admin: bool = False
) -> models.User:
    hashed_password = utils.get_password_hash(user.password1)
    try:
        db_user = models.User(
            username=user.username,
            email=user.email,
            is_admin=is_admin,
            hashed_password=hashed_password,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        raise exceptions.UserDuplicatedError


# OAuth2
def authenticate_user(username: str, password: str, db: Session) -> models.User:
    user = get_user_by_username(db, username)
    if not user or not utils.verify_password(password, user.hashed_password):
        raise exceptions.CredentialsError
    return user
