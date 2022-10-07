from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from onboarding_app import database, dependencies, schemas
from onboarding_app.queries import wishlist as wishlist_query

wishlist_router = APIRouter()


# TODO: login user only
@wishlist_router.post("/wishlists", response_model=schemas.Wishlist)
def create_wishlist(
    wishlist: schemas.WishlistCreate,
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(dependencies.get_current_user),
):
    db_wishlist = wishlist_query.create_wishlist(
        db=db,
        current_user=current_user,
        wishlist=wishlist,
    )
    return jsonable_encoder(db_wishlist)


@wishlist_router.get("/wishlists", response_model=list[schemas.Wishlist])
def fetch_wishlists(
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(dependencies.get_current_user),
):
    db_wishlists = wishlist_query.fetch_wishlists(db=db, current_user=current_user)
    return jsonable_encoder(db_wishlists)


@wishlist_router.get("/wishlists/{wishlist_id}", response_model=schemas.Wishlist)
def get_wishlist(
    wishlist_id: int,
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(dependencies.get_current_user),
):
    db_wishlist = wishlist_query.get_wishlist(
        db=db, wishlist_id=wishlist_id, current_user=current_user
    )
    return jsonable_encoder(db_wishlist)
