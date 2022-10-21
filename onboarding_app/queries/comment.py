from typing import Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from onboarding_app import exceptions, models, schemas


def create_comment(
    db: Session,
    current_user: schemas.User,
    comment: schemas.CommentCreate,
    wishlist_id: int,
    parent_id: Optional[int] = None,
    is_reply: bool = False,
) -> models.Comment:
    try:
        created_comment = models.Comment(
            user_id=current_user.id,
            wishlist_id=wishlist_id,
            body=comment.body,
            parent_id=parent_id,
            is_reply=is_reply,
        )
        db.add(created_comment)
        db.commit()
        db.refresh(created_comment)
    except IntegrityError:
        raise exceptions.DuplicatedError
    return created_comment


def fetch_comments(
    db: Session,
    wishlist_id: int,
    limit: int,
    offset: int,
) -> list[models.Comment]:

    return (
        db.query(models.Comment)
        .filter(models.Comment.wishlist_id == wishlist_id)
        .limit(limit)
        .offset(offset)
        .all()
    )


def fetch_replies(db: Session, wishlist_id: int, parent_id: int):

    db_parent_comment = (
        db.query(models.Comment).filter(models.Comment.id == parent_id).first()
    )
    if not db_parent_comment:
        raise exceptions.DataDoesNotExistError

    db_replies_list = (
        db.query(models.Comment)
        .filter(
            models.Comment.wishlist_id == wishlist_id,
            models.Comment.parent_id == parent_id,
        )
        .all()
    )

    return {
        "comment": db_parent_comment,
        "replies": db_replies_list,
    }


def update_comment(
    db: Session,
    current_user: schemas.User,
    comment: schemas.CommentCreate,
    wishlist_id: int,
    comment_id: int,
) -> models.Comment:

    wishlist_query_res = db.query(models.Wishlist).filter(
        models.Wishlist.id == wishlist_id
    )
    if not wishlist_query_res.first():
        raise exceptions.DataDoesNotExistError

    db_comment = (
        db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    )
    if not db_comment:
        raise exceptions.DataDoesNotExistError
    if db_comment.user_id != current_user.id:
        raise exceptions.PermissionDeniedError
    db_comment.body = comment.body
    db.commit()
    db.refresh(db_comment)
    return db_comment


def delete_comment(
    db: Session,
    current_user: schemas.User,
    wishlist_id: int,
    comment_id: int,
) -> None:

    wishlist_query_res = db.query(models.Wishlist).filter(
        models.Wishlist.id == wishlist_id
    )
    if not wishlist_query_res.first():
        raise exceptions.DataDoesNotExistError

    db_comment = (
        db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    )
    if not db_comment:
        raise exceptions.DataDoesNotExistError
    if db_comment.user_id != current_user.id:
        raise exceptions.PermissionDeniedError
    db.delete(db_comment)
    db.commit()
    return None
