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


def fetch_wishlists(
    db: Session,
    current_user: schemas.User,
    order_by: str,
    limit: str,
    offset: str,
) -> list[models.Wishlist]:

    # TODO: add pagination
    if limit is None:
        limit = "10"
    if offset is None:
        offset = "0"

    db_wishlists = db.query(models.Wishlist).filter(
        models.Wishlist.user_id == current_user.id
    )

    if order_by == "created":
        return (
            db_wishlists.order_by(models.Wishlist.created_date.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )
    elif order_by == "updated":
        return (
            db_wishlists.order_by(models.Wishlist.updated_date.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )
    elif order_by == "ordered":
        # TODO: add order-by order_num
        return (
            db_wishlists.order_by(models.Wishlist.order_num.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )
    else:
        raise exceptions.InvalidQueryError


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
