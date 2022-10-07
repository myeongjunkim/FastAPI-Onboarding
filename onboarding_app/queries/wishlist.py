from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from onboarding_app import exceptions, models, schemas


def create_wishlist(
    db: Session, current_user: schemas.User, wishlist: schemas.WishlistCreate
) -> models.Wishlist:
    try:
        count_for_order = (
            db.query(models.Wishlist)
            .filter(models.Wishlist.user_id == current_user.id)
            .count()
        )
        db_wishlist = models.Wishlist(
            user_id=current_user.id,
            name=wishlist.name,
            description=wishlist.description,
            order_num=count_for_order + 1,
        )
        db.add(db_wishlist)
        db.commit()
        db.refresh(db_wishlist)
    except IntegrityError:
        raise exceptions.DuplicatedError
    return db_wishlist


def fetch_wishlists(db: Session, current_user: schemas.User) -> list[models.Wishlist]:
    return (
        db.query(models.Wishlist)
        .filter(models.Wishlist.user_id == current_user.id)
        .all()
    )


def get_wishlist(
    db: Session, wishlist_id: int, current_user: schemas.User
) -> models.Wishlist:
    db_stock = db.query(models.Wishlist).filter(models.Wishlist.id == wishlist_id)
    if not db_stock.first():
        raise exceptions.DataDoesNotExistError
    elif db_stock.first().is_open:
        return db_stock.first()
    elif db_stock.first().id != current_user.id:
        raise exceptions.PermissionDeniedError
    return db_stock.first()
