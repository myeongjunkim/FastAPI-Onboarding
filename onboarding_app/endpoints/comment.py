from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from onboarding_app import database, dependencies, schemas
from onboarding_app.queries import comment as comment_query

comment_router = APIRouter(tags=["comment"])


@comment_router.post(
    "/wishlists/{wishlist_id}/comments", response_model=schemas.Comment
)
def create_comment(
    wishlist_id: int,
    comment: schemas.CommentCreate,
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(dependencies.get_current_user),
):
    db_comment = comment_query.create_comment(
        db=db, current_user=current_user, comment=comment, wishlist_id=wishlist_id
    )
    return db_comment


@comment_router.post(
    "/wishlists/{wishlist_id}/comments/{comment_id}", response_model=schemas.Comment
)
def create_reply(
    wishlist_id: int,
    comment_id: int,
    comment: schemas.CommentCreate,
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(dependencies.get_current_user),
):
    db_comment = comment_query.create_comment(
        db=db,
        current_user=current_user,
        comment=comment,
        wishlist_id=wishlist_id,
        parent_id=comment_id,
        is_reply=True,
    )
    return db_comment


# @comment_router.get(
#     "/wishlists/{wishlist_id}}/comments", response_model=list[schemas.Comment]
# )
