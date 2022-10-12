from fastapi import APIRouter, Depends, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from onboarding_app import database, dependencies, schemas
from onboarding_app.queries import wishlist as wishlist_query

wishlist_router = APIRouter(tags=["wishlist"])


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
    order_by: str = Query(default="created"),
    limit: str = Query(default="10"),
    offset: str = Query(default="0"),
):
    db_wishlists = wishlist_query.fetch_wishlists(
        db=db, current_user=current_user, order_by=order_by, limit=limit, offset=offset
    )
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


@wishlist_router.put("/wishlists/{wishlist_id}", response_model=schemas.Wishlist)
def update_wishlist(
    wishlist_id: int,
    wishlist: schemas.WishlistUpdate,
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(dependencies.get_current_user),
):
    db_wishlist = wishlist_query.update_wishlist(
        db=db,
        wishlist_id=wishlist_id,
        current_user=current_user,
        wishlist=wishlist,
    )
    return jsonable_encoder(db_wishlist)


@wishlist_router.delete("/wishlists/{wishlist_id}", response_model=schemas.Wishlist)
def delete_wishlist(
    wishlist_id: int,
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(dependencies.get_current_user),
):
    wishlist_query.delete_wishlist(
        db=db, wishlist_id=wishlist_id, current_user=current_user
    )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Wishlist deleted successfully"},
    )


@wishlist_router.put("/wishlists/{wishlist_id}/order", response_model=schemas.Wishlist)
def change_wishlist_order(
    wishlist_id: int,
    hope_order: int,
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(dependencies.get_current_user),
):
    updated_wishlist = wishlist_query.change_wishlist_order(
        db=db, wishlist_id=wishlist_id, current_user=current_user, hope_order=hope_order
    )
    return jsonable_encoder(updated_wishlist)
