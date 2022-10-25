import pytest

from onboarding_app import models, schemas
from onboarding_app.queries import user as user_query, wishlist as wishlist_query
from onboarding_app.tests.conftest import client, TestingSessionLocal
from onboarding_app.tests.utils import get_wishlist_by_name

db = TestingSessionLocal()
client.authenticate("reg1")


@pytest.fixture(autouse=True)
def create_dumy_data_to_fakedb():
    _create_stocks()
    _create_wishlists()
    _add_wishstock_in_wishlist1()


def _create_stocks():
    for i in range(10):
        stock = models.Stock(
            name=f"stock{i}",
            code=f"code{i}",
            price=(i + 1) * 1000,
            market="KOSPI",
        )
        db.add(stock)
        db.commit()
        db.refresh(stock)


def _create_wishlists():

    reg = user_query.get_user_by_username(db=db, username="reg1")
    wishlist1 = schemas.WishlistCreate(
        name="wishlist1",
        description="wishlist1 description",
    )
    wishlist2 = schemas.WishlistCreate(
        name="wishlist2",
        description="wishlist2 description",
    )
    wishlist_query.create_wishlist(db=db, current_user=reg, wishlist=wishlist1)
    wishlist_query.create_wishlist(db=db, current_user=reg, wishlist=wishlist2)


def _add_wishstock_in_wishlist1():
    reg = user_query.get_user_by_username(db=db, username="reg1")

    wishlist1 = get_wishlist_by_name(db=db, current_user=reg, name="wishlist1")
    for i in range(10):
        wishlist_query.add_stock_to_wishlist(
            db=db,
            current_user=reg,
            wishlist_id=wishlist1.id,
            wishstock=schemas.WishStockCreate(
                stock_id=i + 1,
                purchase_price=(i + 1) * 12000,
                holding_num=i * 10,
            ),
        )


def test_add_stock_to_wishlist2():
    # Given
    reg = user_query.get_user_by_username(db=db, username="reg1")
    wishlist = get_wishlist_by_name(db=db, current_user=reg, name="wishlist2")

    stock = db.query(models.Stock).first()

    # When
    stock_response = client.post(
        f"/wishlists/{wishlist.id}/stocks",
        json={"stock_id": stock.id, "purchase_price": 12332, "holding_num": 10},
    )

    # Then
    assert stock_response.status_code == 200
    assert stock_response.json()["stock"]["name"] == stock.name


def test_add_stock_to_wishlist_fail_case():
    # Given

    reg = user_query.get_user_by_username(db=db, username="reg1")
    wishlist = get_wishlist_by_name(db=db, current_user=reg, name="wishlist2")

    # When
    stock_response = client.post(
        f"/wishlists/{wishlist.id}/stocks",
        json={
            "stock_id": 500000,
            "purchase_price": 12332,
            "holding_num": 10,
        },
    )

    # Then
    assert stock_response.status_code == 404


def test_fetch_stock_in_wishlist():
    # Given
    reg = user_query.get_user_by_username(db=db, username="reg1")
    wishlist = get_wishlist_by_name(db=db, current_user=reg, name="wishlist1")

    # When
    stock_response = client.get(
        f"/wishlists/{wishlist.id}/stocks",
    )

    # Then
    assert stock_response.status_code == 200
    assert len(stock_response.json()) == 10


def test_get_stock_in_wishlist():
    # Given
    reg = user_query.get_user_by_username(db=db, username="reg1")
    wishlist = get_wishlist_by_name(db=db, current_user=reg, name="wishlist1")

    stock = db.query(models.Stock).first()

    # When
    stock_response = client.get(
        f"/wishlists/{wishlist.id}/stocks/{stock.id}",
    )

    # Then
    assert stock_response.status_code == 200
    assert stock_response.json()["stock"]["name"] == stock.name


def test_update_stock_in_wishlist():
    # Given
    reg = user_query.get_user_by_username(db=db, username="reg1")
    wishlist = get_wishlist_by_name(db=db, current_user=reg, name="wishlist1")

    stock = db.query(models.Stock).first()

    # When
    stock_response = client.put(
        f"/wishlists/{wishlist.id}/stocks/{stock.id}",
        json={"purchase_price": 120000, "holding_num": 100},
    )

    # Then
    assert stock_response.status_code == 200
    assert stock_response.json()["purchase_price"] == 120000
    assert stock_response.json()["holding_num"] == 100


def test_delete_stock_in_wishlist():
    # Given

    reg = user_query.get_user_by_username(db=db, username="reg1")
    wishlist = get_wishlist_by_name(db=db, current_user=reg, name="wishlist1")

    stock = db.query(models.Stock).first()

    # When
    stock_response = client.delete(
        f"/wishlists/{wishlist.id}/stocks/{stock.id}",
    )

    # Then
    deleted_wishstock_query_res = db.query(models.WishlistXstock).filter(
        models.WishlistXstock.wishlist_id == wishlist.id,
        models.WishlistXstock.stock_id == stock.id,
    )

    assert stock_response.status_code == 200
    assert deleted_wishstock_query_res.first() is None


@pytest.mark.parametrize(
    "origin_order, hope_order",
    (
        # 범위 내에서 정렬
        (2, 7),  # Case 1. 낮은 순서에서 높은 순서로 올라가는 경우
        (5, 2),  # Case 2. 높은 순서에서 낮은 순서로 내려가는 경우
        (3, 3),  # Case 3. 같은 순서로 정렬하는 경우
    ),
)
def test_change_stock_order(origin_order: int, hope_order: int):
    # Given
    reg = user_query.get_user_by_username(db=db, username="reg1")
    wishlist = get_wishlist_by_name(db=db, current_user=reg, name="wishlist1")

    print(wishlist.user_id, reg.id)
    stocks = db.query(models.Stock).limit(10).offset(0).all()

    target_wishstock = (
        db.query(models.WishlistXstock)
        .filter(
            models.WishlistXstock.wishlist_id == wishlist.id,
            models.WishlistXstock.order_num == origin_order,
        )
        .first()
    )

    # When
    stock_order_response = client.put(
        f"/wishlists/{wishlist.id}/stocks/{target_wishstock.stock_id}/order",
        params={"hope_order": hope_order},
    )

    # Then
    assert stock_order_response.status_code == 200
    assert stock_order_response.json()["order_num"] == hope_order

    wishstocks_ordered_by_order_num = (
        db.query(models.WishlistXstock)
        .filter(
            models.WishlistXstock.wishlist_id == wishlist.id,
        )
        .order_by(models.WishlistXstock.order_num)
        .all()
    )

    for i, wishstock in enumerate(wishstocks_ordered_by_order_num):

        if i < min(origin_order, hope_order) or i > max(origin_order, hope_order):
            assert wishstock.stock_id == stocks[i].id
        elif i == hope_order:
            assert wishstock.stock_id == stocks[origin_order].id
        else:
            gap = 1 if origin_order < hope_order else -1
            assert wishstock.stock_id == stocks[i].id + gap
