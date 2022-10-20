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
