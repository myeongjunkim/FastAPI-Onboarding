from typing import Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from onboarding_app import exceptions, models, schemas


def _get_comment_response(db: Session, comment: models.Comment):
    return schemas.Comment(
        id=comment.id,
        user_id=comment.user_id,
        wishlist_id=comment.wishlist_id,
        body=comment.body,
        is_reply=comment.is_reply,
        parent_id=comment.parent_id,
        history=jsonable_encoder(
            db.query(models.History)
            .filter(models.History.comment_id == comment.id)
            .order_by(text("created_at desc"))
            .all()
        ),
    )


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
    created_history = models.History(comment_id=created_comment.id, body=comment.body)
    db.add(created_history)
    db.commit()
    db.refresh(created_history)
    return _get_comment_response(db=db, comment=created_comment)


def fetch_comments(
    db: Session,
    wishlist_id: int,
    limit: int,
    offset: int,
) -> list[models.Comment]:

    db_comment_list = (
        db.query(models.Comment)
        .filter(models.Comment.wishlist_id == wishlist_id)
        .limit(limit)
        .offset(offset)
        .all()
    )
    return list(
        map(
            lambda comment: _get_comment_response(db=db, comment=comment),
            db_comment_list,
        )
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
        "comment": _get_comment_response(db, db_parent_comment),
        "replies": list(
            map(
                lambda comment: _get_comment_response(db=db, comment=comment),
                db_replies_list,
            )
        ),
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

    created_history = models.History(
        comment_id=db_comment.id,
        body=comment.body,
    )

    db.commit()
    db.refresh(db_comment)

    db.add(created_history)
    db.commit()

    return _get_comment_response(db, db_comment)


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
