from datetime import datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Query, Session

from onboarding_app import exceptions, models, schemas


def _check_wishlist_exist_and_access_permission(
    db_wishlist: Query, current_user: schemas.User
):
    if not db_wishlist.first():
        raise exceptions.DataDoesNotExistError
    elif db_wishlist.first().user_id != current_user.id:
        raise exceptions.PermissionDeniedError


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
            order_num=count_for_order,
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
    desc: bool,
    limit: int,
    offset: int,
) -> list[models.Wishlist]:

    order_column = models.Wishlist.__table__.columns.get(order_by)
    if desc:
        order_column = order_column.desc()
    return (
        db.query(models.Wishlist)
        .filter(models.Wishlist.user_id == current_user.id)
        .order_by(order_column)
        .limit(limit)
        .offset(offset)
        .all()
    )


def get_wishlist(
    db: Session, wishlist_id: int, current_user: schemas.User
) -> models.Wishlist:
    db_wishlist = db.query(models.Wishlist).filter(models.Wishlist.id == wishlist_id)
    if not db_wishlist.first():
        raise exceptions.DataDoesNotExistError
    elif db_wishlist.first().is_open or db_wishlist.first().user_id == current_user.id:
        return db_wishlist.first()
    else:
        raise exceptions.PermissionDeniedError


def update_wishlist(
    db: Session,
    wishlist_id: int,
    current_user: schemas.User,
    wishlist: schemas.WishlistUpdate,
) -> models.Wishlist:
    db_wishlist = db.query(models.Wishlist).filter(models.Wishlist.id == wishlist_id)
    _check_wishlist_exist_and_access_permission(db_wishlist, current_user)
    try:
        db_wishlist.update(wishlist.dict(exclude_unset=True))
        db_wishlist.first().updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_wishlist.first())
    except IntegrityError:
        raise exceptions.DuplicatedError
    return db_wishlist.first()


def delete_wishlist(
    db: Session, wishlist_id: int, current_user: schemas.User
) -> models.Wishlist:
    db_wishlist = db.query(models.Wishlist).filter(models.Wishlist.id == wishlist_id)
    _check_wishlist_exist_and_access_permission(db_wishlist, current_user)
    db_wishlist.delete()
    db.commit()
    _reorder_order_num(db, current_user.id)
    return db_wishlist.first()


def _reorder_order_num(db: Session, user_id: int):
    users_db_wishlist = (
        db.query(models.Wishlist)
        .filter(models.Wishlist.user_id == user_id)
        .order_by(models.Wishlist.order_num)
    )
    for i, wishlist in enumerate(users_db_wishlist):
        wishlist.order_num = i
    db.commit()


def change_wishlist_order(
    db: Session,
    current_user: schemas.User,
    wishlist_id: int,
    hope_order: int,
) -> models.Wishlist:
    db_wishlist = db.query(models.Wishlist).filter(models.Wishlist.id == wishlist_id)
    users_db_wishlist = db.query(models.Wishlist).filter(
        models.Wishlist.user_id == current_user.id
    )

    _check_wishlist_exist_and_access_permission(db_wishlist, current_user)
    if hope_order < 0 or hope_order >= users_db_wishlist.count():
        raise exceptions.InvalidQueryError

    origin_order = db_wishlist.first().order_num
    if hope_order > origin_order:
        _update_upper_num_order(db, current_user, origin_order, hope_order)

    elif hope_order < origin_order:
        _update_lower_num_order(db, current_user, origin_order, hope_order)
    db_wishlist.first().order_num = hope_order
    db.commit()
    return db_wishlist.first()


def _update_upper_num_order(
    db: Session, current_user: schemas.User, origin_order: int, hope_order: int
):
    db.query(models.Wishlist).filter(
        models.Wishlist.order_num > origin_order,
        models.Wishlist.order_num <= hope_order,
        models.Wishlist.user_id == current_user.id,
    ).update(
        {models.Wishlist.order_num: models.Wishlist.order_num - 1},
        synchronize_session=False,
    )


def _update_lower_num_order(
    db: Session, current_user: schemas.User, origin_order: int, hope_order: int
):
    db.query(models.Wishlist).filter(
        models.Wishlist.order_num < origin_order,
        models.Wishlist.order_num >= hope_order,
        models.Wishlist.user_id == current_user.id,
    ).update(
        {models.Wishlist.order_num: models.Wishlist.order_num + 1},
        synchronize_session=False,
    )
