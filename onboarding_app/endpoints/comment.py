from fastapi import APIRouter, Depends, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
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

    return comment_query.create_comment(
        db=db, current_user=current_user, comment=comment, wishlist_id=wishlist_id
    )


@comment_router.get(
    "/wishlists/{wishlist_id}/comments", response_model=list[schemas.Comment]
)
def fetch_comments(
    *,
    db: Session = Depends(database.get_db),
    wishlist_id: int,
    limit: int = Query(default=10),
    offset: int = Query(default=0),
):

    return comment_query.fetch_comments(
        db=db,
        wishlist_id=wishlist_id,
        limit=limit,
        offset=offset,
    )


@comment_router.get(
    "/wishlists/{wishlist_id}/comments/{comment_id}", response_model=schemas.Comment
)
def get_comment(
    wishlist_id: int,
    comment_id: int,
    db: Session = Depends(database.get_db),
):
    db_comment = comment_query.get_comment(
        db=db,
        wishlist_id=wishlist_id,
        comment_id=comment_id,
    )
    return db_comment


@comment_router.put(
    "/wishlists/{wishlist_id}/comments/{comment_id}", response_model=schemas.Comment
)
def update_comment(
    wishlist_id: int,
    comment_id: int,
    comment: schemas.CommentCreate,
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(dependencies.get_current_user),
):
    db_comment = comment_query.update_comment(
        db=db,
        current_user=current_user,
        comment=comment,
        wishlist_id=wishlist_id,
        comment_id=comment_id,
    )
    return db_comment


@comment_router.delete(
    "/wishlists/{wishlist_id}/comments/{comment_id}",
)
def delete_comment(
    wishlist_id: int,
    comment_id: int,
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(dependencies.get_current_user),
):
    comment_query.delete_comment(
        db=db,
        current_user=current_user,
        wishlist_id=wishlist_id,
        comment_id=comment_id,
    )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Wishlist deleted successfully"},
    )


@comment_router.post(
    "/wishlists/{wishlist_id}/comments/{comment_id}/replies",
    response_model=schemas.Comment,
)
def create_reply_to_comment(
    wishlist_id: int,
    comment_id: int,
    comment: schemas.CommentCreate,
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(dependencies.get_current_user),
):

    return comment_query.create_comment(
        db=db,
        current_user=current_user,
        comment=comment,
        wishlist_id=wishlist_id,
        parent_id=comment_id,
        is_reply=True,
    )


@comment_router.get(
    "/wishlists/{wishlist_id}/comments/{comment_id}/replies",
    response_model=list[schemas.Comment],
)
def fetch_replies(
    wishlist_id: int,
    comment_id: int,
    db: Session = Depends(database.get_db),
):
    return comment_query.fetch_replies(
        db=db,
        wishlist_id=wishlist_id,
        parent_id=comment_id,
    )


@comment_router.get(
    "/wishlists/{wishlist_id}/comments/{comment_id}/history",
    response_model=list[schemas.History],
)
def fetch_history(
    wishlist_id: int,
    comment_id: int,
    db: Session = Depends(database.get_db),
):
    return jsonable_encoder(
        comment_query.fetch_history(
            db=db,
            wishlist_id=wishlist_id,
            comment_id=comment_id,
        )
    )
