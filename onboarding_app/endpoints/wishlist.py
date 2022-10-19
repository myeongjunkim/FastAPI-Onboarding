from typing import Literal

from fastapi import APIRouter, Depends, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from onboarding_app import database, dependencies, schemas
from onboarding_app.queries import wishlist as wishlist_query

wishlist_router = APIRouter(tags=["wishlist"])


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
    sort: Literal["created_at", "updated_at"] = "created_at",
    order_by: Literal["desc", "asc"] = "desc",
    limit: int = Query(default=10),
    offset: int = Query(default=0),
):

    db_wishlists = wishlist_query.fetch_wishlists(
        db=db,
        current_user=current_user,
        sort=sort,
        order_by=order_by,
        limit=limit,
        offset=offset,
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


@wishlist_router.post(
    "/wishlists/{wishlist_id}/wishstocks", response_model=schemas.WishStockResponse
)
def add_stock_to_wishlist(
    wishlist_id: int,
    wishstock: schemas.WishStockCreate,
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(dependencies.get_current_user),
):
    db_wishstock = wishlist_query.add_stock_to_wishlist(
        db=db,
        current_user=current_user,
        wishlist_id=wishlist_id,
        wishstock=wishstock,
    )
    return db_wishstock


@wishlist_router.get(
    "/wishlists/{wishlist_id}/wishstocks",
    response_model=list[schemas.WishStockResponse],
)
def fetch_stock_in_wishlist(
    wishlist_id: int,
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(dependencies.get_current_user),
):
    return wishlist_query.fetch_stock_in_wishlist(
        db=db, current_user=current_user, wishlist_id=wishlist_id
    )


@wishlist_router.get(
    "/wishlists/{wishlist_id}/wishstocks/{wishstock_id}",
    response_model=schemas.WishStockResponse,
)
def get_stock_in_wishlist(
    wishlist_id: int,
    stock_id: int,
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(dependencies.get_current_user),
):
    return wishlist_query.get_stock_in_wishlist(
        db=db,
        current_user=current_user,
        wishlist_id=wishlist_id,
        stock_id=stock_id,
    )


@wishlist_router.put(
    "/wishlists/{wishlist_id}/wishstocks/{wishstock_id}",
    response_model=schemas.WishStockResponse,
)
def update_stock_in_wishlist(
    wishlist_id: int,
    stock_id: int,
    wishstock: schemas.WishStockUpdate,
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(dependencies.get_current_user),
):
    return wishlist_query.update_stock_in_wishlist(
        db=db,
        current_user=current_user,
        wishlist_id=wishlist_id,
        stock_id=stock_id,
        wishstock=wishstock,
    )


@wishlist_router.delete(
    "/wishlists/{wishlist_id}/wishstocks/{wishstock_id}",
    response_model=schemas.WishStockResponse,
)
def delete_stock_in_wishlist(
    wishlist_id: int,
    stock_id: int,
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(dependencies.get_current_user),
):
    wishlist_query.delete_stock_in_wishlist(
        db=db,
        current_user=current_user,
        wishlist_id=wishlist_id,
        stock_id=stock_id,
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "WishlistXstock deleted successfully"},
    )


@wishlist_router.put(
    "/wishlists/{wishlist_id}/wishstocks/{wishstock_id}/order",
    response_model=schemas.WishStockResponse,
)
def change_stock_order(
    wishlist_id: int,
    stock_id: int,
    hope_order: int,
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(dependencies.get_current_user),
):
    return wishlist_query.change_stock_order(
        db=db,
        current_user=current_user,
        wishlist_id=wishlist_id,
        stock_id=stock_id,
        hope_order=hope_order,
    )
