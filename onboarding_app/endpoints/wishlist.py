from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from onboarding_app import database, dependencies, schemas
from onboarding_app.queries import wishlist as wishlist_query

wishlist_router = APIRouter()


# TODO: login user only
@wishlist_router.post("/wishlists", response_model=schemas.WishList)
def create_stock(
    wishlist: schemas.WishListCreate,
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(dependencies.get_current_user),
):
    db_wishlist = wishlist_query.create_wishlist(
        db=db,
        current_user=current_user,
        wishlist=wishlist,
    )
    return jsonable_encoder(db_wishlist)
