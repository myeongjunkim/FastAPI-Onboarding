from datetime import datetime

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Query, Session

from onboarding_app import exceptions, models, schemas


def _check_wishlist_exist_and_access_permission(
    wishlist_query_res: Query, current_user: schemas.User
):
    if not wishlist_query_res.first():
        raise exceptions.DataDoesNotExistError
    elif wishlist_query_res.first().user_id != current_user.id:
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
        created_wishlist = models.Wishlist(
            user_id=current_user.id,
            name=wishlist.name,
            description=wishlist.description,
            order_num=count_for_order,
        )
        db.add(created_wishlist)
        db.commit()
        db.refresh(created_wishlist)
    except IntegrityError:
        raise exceptions.DuplicatedError
    return created_wishlist


def fetch_wishlists(
    db: Session,
    current_user: schemas.User,
    sort: str,
    order_by: str,
    limit: int,
    offset: int,
) -> list[models.Wishlist]:

    return (
        db.query(models.Wishlist)
        .filter(models.Wishlist.user_id == current_user.id)
        .order_by(text(sort + " " + order_by))
        .limit(limit)
        .offset(offset)
        .all()
    )


def get_wishlist(
    db: Session, wishlist_id: int, current_user: schemas.User
) -> models.Wishlist:
    wishlist_query_res = db.query(models.Wishlist).filter(
        models.Wishlist.id == wishlist_id
    )
    if not wishlist_query_res.first():
        raise exceptions.DataDoesNotExistError
    elif (
        wishlist_query_res.first().is_open
        or wishlist_query_res.first().user_id == current_user.id
    ):
        return wishlist_query_res.first()
    else:
        raise exceptions.PermissionDeniedError


def update_wishlist(
    db: Session,
    wishlist_id: int,
    current_user: schemas.User,
    wishlist: schemas.WishlistUpdate,
) -> models.Wishlist:
    wishlist_query_res = db.query(models.Wishlist).filter(
        models.Wishlist.id == wishlist_id
    )
    _check_wishlist_exist_and_access_permission(wishlist_query_res, current_user)
    try:
        wishlist_query_res.update(wishlist.dict(exclude_unset=True))
        wishlist_query_res.first().updated_at = datetime.utcnow()
        db.commit()
        db.refresh(wishlist_query_res.first())
    except IntegrityError:
        raise exceptions.DuplicatedError
    return wishlist_query_res.first()


def delete_wishlist(
    db: Session, wishlist_id: int, current_user: schemas.User
) -> models.Wishlist:
    wishlist_query_res = db.query(models.Wishlist).filter(
        models.Wishlist.id == wishlist_id
    )
    _check_wishlist_exist_and_access_permission(wishlist_query_res, current_user)
    wishlist_query_res.delete()
    db.commit()
    _reorder_wishlist_order_num(db, current_user.id)
    return wishlist_query_res.first()


def _reorder_wishlist_order_num(db: Session, user_id: int):
    users_wishlist_query_res = (
        db.query(models.Wishlist)
        .filter(models.Wishlist.user_id == user_id)
        .order_by(models.Wishlist.order_num)
    )
    for i, wishlist in enumerate(users_wishlist_query_res):
        wishlist.order_num = i
    db.commit()


def change_wishlist_order(
    db: Session,
    current_user: schemas.User,
    wishlist_id: int,
    hope_order: int,
) -> models.Wishlist:
    wishlist_query_res = db.query(models.Wishlist).filter(
        models.Wishlist.id == wishlist_id
    )
    users_wishlist_query_res = db.query(models.Wishlist).filter(
        models.Wishlist.user_id == current_user.id
    )

    _check_wishlist_exist_and_access_permission(wishlist_query_res, current_user)
    if hope_order < 0 or hope_order >= users_wishlist_query_res.count():
        raise exceptions.InvalidQueryError

    origin_order = wishlist_query_res.first().order_num
    if hope_order > origin_order:
        _update_upper_num_order(db, current_user, origin_order, hope_order)

    elif hope_order < origin_order:
        _update_lower_num_order(db, current_user, origin_order, hope_order)
    wishlist_query_res.first().order_num = hope_order
    db.commit()
    return wishlist_query_res.first()


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
