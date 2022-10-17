from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from onboarding_app import exceptions, models, schemas, utils


def get_stock_by_name(stock_name: str, db: Session) -> models.Stock:
    stock_query_res = db.query(models.Stock).filter(models.Stock.name == stock_name)
    return stock_query_res.first()


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

    db_stock = get_stock_by_name(wishlistXstock.stock_name, db)
    if not db_stock:
        raise exceptions.StockNotFoundError

    count_for_order = (
        db.query(models.WishlistXstock)
        .filter(models.WishlistXstock.wishlist_id == wishlist_id)
        .count()
    )

    return_rate = round(
        (db_stock.price - wishlistXstock.purchase_price)
        / wishlistXstock.purchase_price
        * 100,
        2,
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

    return schemas.WishlistXstockResponse(
        wishlist_id=wishlist_id,
        stock_name=db_stock.name,
        order_num=count_for_order,
        purchase_price=wishlistXstock.purchase_price,
        holding_num=wishlistXstock.holding_num,
        last_price=db_stock.price,
        return_rate=return_rate,
    )


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
    for wishlistXstock in wishlistXstocks_query_res:
        stock = (
            db.query(models.Stock)
            .filter(models.Stock.id == wishlistXstock.stock_id)
            .first()
        )
        return_rate = round(
            (stock.price - wishlistXstock.purchase_price)
            / wishlistXstock.purchase_price
            * 100,
            2,
        )
        wishlistXstocks.append(
            schemas.WishlistXstockResponse(
                wishlist_id=wishlist_id,
                stock_name=stock.name,
                order_num=wishlistXstock.order_num,
                purchase_price=wishlistXstock.purchase_price,
                holding_num=wishlistXstock.holding_num,
                last_price=stock.price,
                return_rate=return_rate,
            )
        )

    return wishlistXstocks
