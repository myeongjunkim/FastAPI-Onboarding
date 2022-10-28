from typing import Optional

from sqlalchemy.orm import Session

from onboarding_app import exceptions, models, schemas


def _validate_accessible_wishlist(
    db: Session, wishlist_id: int, current_user: schemas.User
) -> None:
    wishlist = (
        db.query(models.Wishlist).filter(models.Wishlist.id == wishlist_id).first()
    )
    if not wishlist:
        raise exceptions.DataDoesNotExistError
    if not wishlist.is_open and wishlist.user_id != current_user.id:
        raise exceptions.PermissionDeniedError


def _get_accessible_comment(
    db: Session, wishlist_id: int, comment_id: int
) -> models.Comment:
    comment_query_res = db.query(models.Comment).filter(
        models.Comment.wishlist_id == wishlist_id, models.Comment.id == comment_id
    )
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

    _validate_accessible_wishlist(db, wishlist_id, current_user)
    created_comment = models.Comment(
        user_id=current_user.id,
        wishlist_id=wishlist_id,
        content=comment.content,
        parent_id=parent_id,
        is_reply=is_reply,
    )

    db.add(created_comment)
    db.flush()

    created_history = models.History(
        comment_id=created_comment.id, content=created_comment.content
    )

    db.add(created_history)
    db.flush()

    db.commit()
    return created_comment


def fetch_comments(
    db: Session,
    wishlist_id: int,
    current_user: schemas.User,
    limit: int,
    offset: int,
) -> list[models.Comment]:
    _validate_accessible_wishlist(db, wishlist_id, current_user)
    return (
        db.query(models.Comment)
        .filter(models.Comment.wishlist_id == wishlist_id)
        .limit(limit)
        .offset(offset)
        .all()
    )


def get_comment(
    db: Session,
    wishlist_id: int,
    comment_id: int,
    current_user: schemas.User,
) -> models.Comment:
    _validate_accessible_wishlist(db, wishlist_id, current_user)
    db_comment = _get_accessible_comment(db, wishlist_id, comment_id)

    return db_comment


def update_comment(
    db: Session,
    current_user: schemas.User,
    comment: schemas.CommentCreate,
    wishlist_id: int,
    comment_id: int,
) -> models.Comment:

    _validate_accessible_wishlist(db, wishlist_id, current_user)
    db_comment = _get_accessible_comment(db, wishlist_id, comment_id)

    if db_comment.user_id != current_user.id:
        raise exceptions.PermissionDeniedError
    db_comment.content = comment.content

    created_history = models.History(
        comment_id=db_comment.id,
        content=comment.content,
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

    _validate_accessible_wishlist(db, wishlist_id, current_user)
    db_comment = _get_accessible_comment(db, wishlist_id, comment_id)
    if db_comment.user_id != current_user.id:
        raise exceptions.PermissionDeniedError
    db.delete(db_comment)
    db.commit()
    return None


def fetch_replies(
    db: Session, wishlist_id: int, parent_id: int, current_user: schemas.User
) -> list[models.Comment]:

    _validate_accessible_wishlist(db, wishlist_id, current_user)
    parent_comment = _get_accessible_comment(db, wishlist_id, parent_id)

    return parent_comment.replies


def fetch_history(
    db: Session, wishlist_id: int, comment_id: int, current_user: schemas.User
) -> list[models.History]:

    _validate_accessible_wishlist(db, wishlist_id, current_user)
    db_comment = _get_accessible_comment(db, wishlist_id, comment_id)

    return (
        db.query(models.History)
        .filter(
            models.History.comment_id == db_comment.id,
        )
        .order_by(models.History.created_at.desc())
        .all()
    )
