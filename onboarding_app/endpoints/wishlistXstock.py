from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from onboarding_app import database, dependencies, schemas
from onboarding_app.queries import wishlistXstock as wishlistXstock_query

wishlistXstock_router = APIRouter(tags=["stock"])


@wishlistXstock_router.post(
    "/wishlists/{wishlist_id}/stocks", response_model=schemas.WishlistXstockResponse
)
def create_wishlistXstock(
    wishlist_id: int,
    wishlistXstock: schemas.WishlistXstockCreate,
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(dependencies.get_current_user),
):
    db_wishlistXstock = wishlistXstock_query.create_wishlistXstock(
        db=db,
        current_user=current_user,
        wishlist_id=wishlist_id,
        wishlistXstock=wishlistXstock,
    )
    return db_wishlistXstock


@wishlistXstock_router.get(
    "/wishlists/{wishlist_id}/stocks",
    response_model=list[schemas.WishlistXstockResponse],
)
def fetch_wishlistXstocks(
    wishlist_id: int,
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(dependencies.get_current_user),
):
    return wishlistXstock_query.fetch_wishlistXstocks(
        db=db, current_user=current_user, wishlist_id=wishlist_id
    )


@wishlistXstock_router.get(
    "/wishlists/{wishlist_id}/stocks/{stock_id}",
    response_model=schemas.WishlistXstockResponse,
)
def get_wishlistXstock(
    wishlist_id: int,
    wishlistXstock_id: int,
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(dependencies.get_current_user),
):
    return wishlistXstock_query.get_wishlistXstock(
        db=db,
        current_user=current_user,
        wishlist_id=wishlist_id,
        wishlistXstock_id=wishlistXstock_id,
    )


@wishlistXstock_router.put(
    "/wishlists/{wishlist_id}/stocks/{stock_id}",
    response_model=schemas.WishlistXstockResponse,
)
def update_wishlistXstock(
    wishlist_id: int,
    wishlistXstock_id: int,
    wishlistXstock: schemas.WishlistXstockUpdate,
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(dependencies.get_current_user),
):
    return wishlistXstock_query.update_wishlistXstock(
        db=db,
        current_user=current_user,
        wishlist_id=wishlist_id,
        wishlistXstock_id=wishlistXstock_id,
        wishlistXstock=wishlistXstock,
    )


@wishlistXstock_router.delete(
    "/wishlists/{wishlist_id}/stocks/{stock_id}",
    response_model=schemas.WishlistXstockResponse,
)
def delete_wishlistXstock(
    wishlist_id: int,
    wishlistXstock_id: int,
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(dependencies.get_current_user),
):
    wishlistXstock_query.delete_wishlistXstock(
        db=db,
        current_user=current_user,
        wishlist_id=wishlist_id,
        wishlistXstock_id=wishlistXstock_id,
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "WishlistXstock deleted successfully"},
    )


@wishlistXstock_router.put(
    "/wishlists/{wishlist_id}/stocks/{stock_idd}/order",
    response_model=schemas.WishlistXstockResponse,
)
def change_wishlistXstock_order(
    wishlist_id: int,
    wishlistXstock_id: int,
    hope_order: int,
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(dependencies.get_current_user),
):
    return wishlistXstock_query.change_wishlistXstock_order(
        db=db,
        current_user=current_user,
        wishlist_id=wishlist_id,
        wishlistXstock_id=wishlistXstock_id,
        hope_order=hope_order,
    )
