from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from onboarding_app import database, dependencies, schemas
from onboarding_app.queries import wishlistXstock as wishlistXstock_query

wishlistXstock_router = APIRouter(tags=["wishlistXstock"])


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
