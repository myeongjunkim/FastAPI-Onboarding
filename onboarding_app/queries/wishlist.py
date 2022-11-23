from datetime import datetime

from fastapi.encoders import jsonable_encoder
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Query, Session

from onboarding_app import exceptions, models, schemas, utils


def validate_accessible_wishlist(wishlist_query_res: Query, current_user: schemas.User):
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
    except IntegrityError:
        raise exceptions.DuplicatedError
    return get_wishlist(db, created_wishlist.id, current_user)


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
        .order_by(text(f"{sort} {order_by}"))
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
    validate_accessible_wishlist(wishlist_query_res, current_user)
    try:
        wishlist_query_res.update(wishlist.dict(exclude_unset=True))
        wishlist_query_res.first().updated_at = datetime.utcnow()
        db.commit()
    except IntegrityError:
        raise exceptions.DuplicatedError
    return wishlist_query_res.first()


def delete_wishlist(
    db: Session, wishlist_id: int, current_user: schemas.User
) -> models.Wishlist:
    wishlist_query_res = db.query(models.Wishlist).filter(
        models.Wishlist.id == wishlist_id
    )
    validate_accessible_wishlist(wishlist_query_res, current_user)
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
    wishlistList_query_res_by_foreign_key = db.query(models.Wishlist).filter(
        models.Wishlist.user_id == current_user.id
    )

    validate_accessible_wishlist(wishlist_query_res, current_user)

    utils.reorder(
        target_model_obj=wishlist_query_res.first(),
        hope_order=hope_order,
        modelList_query_res_by_foreign_key=wishlistList_query_res_by_foreign_key,
    )

    db.commit()
    return wishlist_query_res.first()


def _get_wishstock_response(
    db_wishstock: schemas.WishStock,
    db_stock: schemas.Stock,
) -> schemas.WishStockResponse:

    return_rate = round(
        (db_stock.price - db_wishstock.purchase_price)
        / db_wishstock.purchase_price
        * 100,
        2,
    )

    return schemas.WishStockResponse(
        stock=jsonable_encoder(db_stock),
        order_num=db_wishstock.order_num,
        purchase_price=db_wishstock.purchase_price,
        holding_num=db_wishstock.holding_num,
        return_rate=return_rate,
    )


def add_stock_to_wishlist(
    db: Session,
    current_user: schemas.User,
    wishlist_id: int,
    wishstock: schemas.WishStockCreate,
) -> schemas.WishStockResponse:

    wishlist_query_res = db.query(models.Wishlist).filter(
        models.Wishlist.id == wishlist_id
    )
    validate_accessible_wishlist(wishlist_query_res, current_user)

    db_stock = (
        db.query(models.Stock).filter(models.Stock.id == wishstock.stock_id).first()
    )
    if not db_stock:
        raise exceptions.StockNotFoundError

    count_for_order = (
        db.query(models.WishlistXstock)
        .filter(models.WishlistXstock.wishlist_id == wishlist_id)
        .count()
    )

    try:
        created_wishstock = models.WishlistXstock(
            wishlist_id=wishlist_id,
            stock_id=db_stock.id,
            purchase_price=wishstock.purchase_price,
            holding_num=wishstock.holding_num,
            order_num=count_for_order,
        )
        db.add(created_wishstock)
        db.commit()
    except ZeroDivisionError:
        raise exceptions.InvalidQueryError
    except IntegrityError:
        raise exceptions.DuplicatedError

    return _get_wishstock_response(created_wishstock, db_stock)


def fetch_stock_in_wishlist(
    db: Session,
    current_user: schemas.User,
    wishlist_id: int,
) -> list[schemas.WishStockResponse]:

    wishlist_query_res = db.query(models.Wishlist).filter(
        models.Wishlist.id == wishlist_id
    )
    validate_accessible_wishlist(wishlist_query_res, current_user)

    wishstocks_query_res = (
        db.query(models.WishlistXstock)
        .filter(models.WishlistXstock.wishlist_id == wishlist_id)
        .order_by(models.WishlistXstock.order_num)
        .all()
    )

    wishstocks = []
    for db_wishstock in wishstocks_query_res:
        db_stock = (
            db.query(models.Stock)
            .filter(models.Stock.id == db_wishstock.stock_id)
            .first()
        )

        wishstocks.append(_get_wishstock_response(db_wishstock, db_stock))

    return wishstocks


def get_stock_in_wishlist(
    db: Session,
    current_user: schemas.User,
    wishlist_id: int,
    stock_id: int,
) -> schemas.WishStockResponse:

    wishlist_query_res = db.query(models.Wishlist).filter(
        models.Wishlist.id == wishlist_id
    )
    validate_accessible_wishlist(wishlist_query_res, current_user)

    wishstock_query_res = db.query(models.WishlistXstock).filter(
        models.WishlistXstock.wishlist_id == wishlist_id,
        models.WishlistXstock.stock_id == stock_id,
    )

    if not wishstock_query_res.first():
        raise exceptions.DataDoesNotExistError

    db_wishstock = wishstock_query_res.first()
    db_stock = db.query(models.Stock).filter(models.Stock.id == stock_id).first()

    return _get_wishstock_response(db_wishstock, db_stock)


def update_stock_in_wishlist(
    db: Session,
    current_user: schemas.User,
    wishlist_id: int,
    stock_id: int,
    wishstock: schemas.WishStockUpdate,
) -> schemas.WishStockResponse:

    wishlist_query_res = db.query(models.Wishlist).filter(
        models.Wishlist.id == wishlist_id
    )
    validate_accessible_wishlist(wishlist_query_res, current_user)

    wishstock_query_res = db.query(models.WishlistXstock).filter(
        models.WishlistXstock.wishlist_id == wishlist_id,
        models.WishlistXstock.stock_id == stock_id,
    )

    if not wishstock_query_res.first():
        raise exceptions.DataDoesNotExistError

    wishstock_query_res.update(wishstock.dict(exclude_unset=True))
    db.commit()

    db_wishstock = wishstock_query_res.first()
    db_stock = db.query(models.Stock).filter(models.Stock.id == stock_id).first()

    return _get_wishstock_response(db_wishstock, db_stock)


def delete_stock_in_wishlist(
    db: Session,
    current_user: schemas.User,
    wishlist_id: int,
    stock_id: int,
) -> None:

    wishlist_query_res = db.query(models.Wishlist).filter(
        models.Wishlist.id == wishlist_id
    )
    validate_accessible_wishlist(wishlist_query_res, current_user)

    wishstock_query_res = db.query(models.WishlistXstock).filter(
        models.WishlistXstock.wishlist_id == wishlist_id,
        models.WishlistXstock.stock_id == stock_id,
    )

    if not wishstock_query_res.first():
        raise exceptions.DataDoesNotExistError

    wishstock_query_res.delete()
    db.commit()
    _reorder_wishstock_for_delete(db, wishlist_id)

    return None


def _reorder_wishstock_for_delete(db: Session, wishlist_id: int):
    users_wishlist_query_res = (
        db.query(models.WishlistXstock)
        .filter(models.WishlistXstock.wishlist_id == wishlist_id)
        .order_by(models.WishlistXstock.order_num)
    )
    for i, wishstock in enumerate(users_wishlist_query_res):
        wishstock.order_num = i
    db.commit()


def change_stock_order(
    db: Session,
    current_user: schemas.User,
    wishlist_id: int,
    stock_id: int,
    hope_order: int,
) -> schemas.WishStockResponse:
    wishlist_query_res = db.query(models.Wishlist).filter(
        models.Wishlist.id == wishlist_id
    )
    validate_accessible_wishlist(wishlist_query_res, current_user)

    wishstockList_query_res_by_foreign_key = db.query(models.WishlistXstock).filter(
        models.WishlistXstock.wishlist_id == wishlist_id
    )

    wishstock_query_res = wishstockList_query_res_by_foreign_key.filter(
        models.WishlistXstock.stock_id == stock_id
    )

    utils.reorder(
        target_model_obj=wishstock_query_res.first(),
        hope_order=hope_order,
        modelList_query_res_by_foreign_key=wishstockList_query_res_by_foreign_key,
    )
    db.commit()

    db_wishstock = wishstock_query_res.first()
    db_stock = db.query(models.Stock).filter(models.Stock.id == stock_id).first()

    return _get_wishstock_response(db_wishstock, db_stock)
