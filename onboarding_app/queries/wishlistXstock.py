from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from onboarding_app import exceptions, models, schemas, utils


def _get_stock_by_name(stock_name: str, db: Session) -> models.Stock:
    stock_query_res = db.query(models.Stock).filter(models.Stock.name == stock_name)
    return stock_query_res.first()


def _get_wishlistXstock_response(
    db_wishlistXstock: models.WishlistXstock, db_stock: models.Stock, db: Session
) -> schemas.WishlistXstockResponse:

    return_rate = round(
        (db_stock.price - db_wishlistXstock.purchase_price)
        / db_wishlistXstock.purchase_price
        * 100,
        2,
    )

    return schemas.WishlistXstockResponse(
        wishlist_id=db_wishlistXstock.wishlist_id,
        stock_name=db_stock.name,
        order_num=db_wishlistXstock.order_num,
        purchase_price=db_wishlistXstock.purchase_price,
        holding_num=db_wishlistXstock.holding_num,
        last_price=db_stock.price,
        return_rate=return_rate,
    )


def create_wishlistXstock(
    db: Session,
    current_user: schemas.User,
    wishlist_id: int,
    wishlistXstock: schemas.WishlistXstockCreate,
) -> schemas.WishlistXstockResponse:

    wishlist_query_res = db.query(models.Wishlist).filter(
        models.Wishlist.id == wishlist_id
    )
    utils.check_wishlist_exist_and_access_permission(wishlist_query_res, current_user)

    db_stock = _get_stock_by_name(wishlistXstock.stock_name, db)
    if not db_stock:
        raise exceptions.StockNotFoundError

    count_for_order = (
        db.query(models.WishlistXstock)
        .filter(models.WishlistXstock.wishlist_id == wishlist_id)
        .count()
    )

    try:
        created_wishlistXstock = models.WishlistXstock(
            wishlist_id=wishlist_id,
            stock_id=db_stock.id,
            purchase_price=wishlistXstock.purchase_price,
            holding_num=wishlistXstock.holding_num,
            order_num=count_for_order,
        )
        db.add(created_wishlistXstock)
        db.commit()
        db.refresh(created_wishlistXstock)
    except ZeroDivisionError:
        raise exceptions.InvalidQueryError
    except IntegrityError:
        raise exceptions.DuplicatedError

    return _get_wishlistXstock_response(created_wishlistXstock, db_stock, db)


def fetch_wishlistXstocks(
    db: Session,
    current_user: schemas.User,
    wishlist_id: int,
) -> list[schemas.WishlistXstockResponse]:

    wishlist_query_res = db.query(models.Wishlist).filter(
        models.Wishlist.id == wishlist_id
    )
    utils.check_wishlist_exist_and_access_permission(wishlist_query_res, current_user)

    wishlistXstocks_query_res = (
        db.query(models.WishlistXstock)
        .filter(models.WishlistXstock.wishlist_id == wishlist_id)
        .order_by(models.WishlistXstock.order_num)
        .all()
    )

    wishlistXstocks = []
    for db_wishlistXstock in wishlistXstocks_query_res:
        db_stock = (
            db.query(models.Stock)
            .filter(models.Stock.id == db_wishlistXstock.stock_id)
            .first()
        )

        wishlistXstocks.append(
            _get_wishlistXstock_response(db_wishlistXstock, db_stock, db)
        )

    return wishlistXstocks


def get_wishlistXstock(
    db: Session,
    current_user: schemas.User,
    wishlist_id: int,
    wishlistXstock_id: int,
) -> schemas.WishlistXstockResponse:

    wishlist_query_res = db.query(models.Wishlist).filter(
        models.Wishlist.id == wishlist_id
    )
    utils.check_wishlist_exist_and_access_permission(wishlist_query_res, current_user)

    wishlistXstock_query_res = db.query(models.WishlistXstock).filter(
        models.WishlistXstock.wishlist_id == wishlist_id,
        models.WishlistXstock.id == wishlistXstock_id,
    )

    if not wishlistXstock_query_res.first():
        raise exceptions.DataDoesNotExistError

    db_wishlistXstock = wishlistXstock_query_res.first()
    db_stock = (
        db.query(models.Stock)
        .filter(models.Stock.id == db_wishlistXstock.stock_id)
        .first()
    )

    return _get_wishlistXstock_response(db_wishlistXstock, db_stock, db)


def update_wishlistXstock(
    db: Session,
    current_user: schemas.User,
    wishlist_id: int,
    wishlistXstock_id: int,
    wishlistXstock: schemas.WishlistXstockUpdate,
) -> schemas.WishlistXstockResponse:

    wishlist_query_res = db.query(models.Wishlist).filter(
        models.Wishlist.id == wishlist_id
    )
    utils.check_wishlist_exist_and_access_permission(wishlist_query_res, current_user)

    wishlistXstock_query_res = db.query(models.WishlistXstock).filter(
        models.WishlistXstock.wishlist_id == wishlist_id,
        models.WishlistXstock.id == wishlistXstock_id,
    )

    if not wishlistXstock_query_res.first():
        raise exceptions.DataDoesNotExistError

    wishlistXstock_query_res.update(wishlistXstock.dict(exclude_unset=True))
    db.commit()
    db.refresh(wishlistXstock_query_res.first())

    db_wishlistXstock = wishlistXstock_query_res.first()
    db_stock = (
        db.query(models.Stock)
        .filter(models.Stock.id == db_wishlistXstock.stock_id)
        .first()
    )

    return _get_wishlistXstock_response(db_wishlistXstock, db_stock, db)
