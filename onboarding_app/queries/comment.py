from typing import Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from onboarding_app import exceptions, models, schemas


def _validate_accessible_wishlist(db: Session, wishlist_id: int) -> None:
    wishlist_query_res = db.query(models.Wishlist).filter(
        models.Wishlist.id == wishlist_id
    )
    if not wishlist_query_res.first():
        raise exceptions.DataDoesNotExistError


def _get_accessible_comment(db: Session, comment_id: int) -> models.Comment:
    comment_query_res = db.query(models.Comment).filter(models.Comment.id == comment_id)
    if not comment_query_res.first():
        raise exceptions.DataDoesNotExistError
    return comment_query_res.first()


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
        db.flush()
    except IntegrityError:
        raise exceptions.DuplicatedError
    created_history = models.History(comment_id=created_comment.id, body=comment.body)
    db.add(created_history)
    db.flush()
    db.commit()
    return created_comment


def fetch_comments(
    db: Session,
    wishlist_id: int,
    limit: int,
    offset: int,
) -> list[models.Comment]:
    _validate_accessible_wishlist(db, wishlist_id)
    return (
        db.query(models.Comment)
        .filter(models.Comment.wishlist_id == wishlist_id)
        .limit(limit)
        .offset(offset)
        .all()
    )


def get_comment(db: Session, wishlist_id: int, comment_id: int) -> models.Comment:
    _validate_accessible_wishlist(db, wishlist_id)
    return db.query(models.Comment).filter(models.Comment.id == comment_id).first()


def update_comment(
    db: Session,
    current_user: schemas.User,
    comment: schemas.CommentCreate,
    wishlist_id: int,
    comment_id: int,
) -> models.Comment:

    _validate_accessible_wishlist(db, wishlist_id)
    db_comment = _get_accessible_comment(db, comment_id)

    if db_comment.user_id != current_user.id:
        raise exceptions.PermissionDeniedError
    db_comment.body = comment.body

    created_history = models.History(
        comment_id=db_comment.id,
        body=comment.body,
    )

    db.add(created_history)
    db.commit()

    return db_comment


def delete_comment(
    db: Session,
    current_user: schemas.User,
    wishlist_id: int,
    comment_id: int,
) -> None:

    _validate_accessible_wishlist(db, wishlist_id)
    db_comment = _get_accessible_comment(db, comment_id)
    if db_comment.user_id != current_user.id:
        raise exceptions.PermissionDeniedError
    db.delete(db_comment)
    db.commit()
    return None


def fetch_replies(db: Session, wishlist_id: int, parent_id: int):

    _validate_accessible_wishlist(db, wishlist_id)

    return (
        db.query(models.Comment)
        .filter(
            models.Comment.wishlist_id == wishlist_id,
            models.Comment.parent_id == parent_id,
        )
        .all()
    )


def fetch_history(
    db: Session, wishlist_id: int, comment_id: int
) -> list[models.History]:

    _validate_accessible_wishlist(db, wishlist_id)

    return (
        db.query(models.History)
        .filter(
            models.History.comment_id == comment_id,
        )
        .order_by(models.History.created_at.desc())
        .all()
    )
