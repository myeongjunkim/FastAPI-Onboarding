import pytest

from onboarding_app import models, schemas
from onboarding_app.queries import user as user_query, wishlist as wishlist_query
from onboarding_app.tests.conftest import client, engine, TestingSessionLocal
from onboarding_app.tests.utils import get_wishlist_by_name, obtain_token_reg1
from scripts.upsert_stock import fetch_stocks, upsert_stock


@pytest.fixture(autouse=True)
def upsert_stock_to_fakedb():
    new_stock_list = fetch_stocks(file_path="./resources/data_1205_20220930.csv")
    upsert_stock(stock_list=new_stock_list, db=engine)


@pytest.fixture(autouse=True)
def create_wishlist():
    db = TestingSessionLocal()
    reg1 = user_query.get_user_by_username(db=db, username="reg1")
    wishlist1 = schemas.WishlistCreate(
        name="wishlist1",
        description="wishlist1 description",
    )

    wishlist_query.create_wishlist(db=db, current_user=reg1, wishlist=wishlist1)


def test_add_stock_to_wishlist():
    # Given
    db = TestingSessionLocal()
    reg1 = user_query.get_user_by_username(db=db, username="reg1")
    reg1_token = obtain_token_reg1()
    wishlist1 = get_wishlist_by_name(db=db, current_user=reg1, name="wishlist1")

    db_stock = db.query(models.Stock).filter(models.Stock.id == 1).first()

    # When
    stock_response = client.post(
        f"/wishlists/{wishlist1.id}/stocks",
        json={"stock_id": db_stock.id, "purchase_price": 12332, "holding_num": 10},
        headers={"Authorization": "Bearer " + reg1_token},
    )

    # Then
    assert stock_response.status_code == 200
    assert stock_response.json()["stock"]["name"] == db_stock.name


def test_add_stock_to_wishlist_fail_case():
    # Given
    db = TestingSessionLocal()
    reg1 = user_query.get_user_by_username(db=db, username="reg1")
    reg1_token = obtain_token_reg1()
    wishlist1 = get_wishlist_by_name(db=db, current_user=reg1, name="wishlist1")

    # When
    stock_response = client.post(
        f"/wishlists/{wishlist1.id}/stocks",
        json={
            "stock_id": 500000,
            "purchase_price": 12332,
            "holding_num": 10,
        },
        headers={"Authorization": "Bearer " + reg1_token},
    )

    # Then
    assert stock_response.status_code == 404


def test_fetch_stock_in_wishlist():
    # Given
    db = TestingSessionLocal()
    reg1 = user_query.get_user_by_username(db=db, username="reg1")
    reg1_token = obtain_token_reg1()
    wishlist1 = get_wishlist_by_name(db=db, current_user=reg1, name="wishlist1")

    db_wishstock_list = db.query(models.Stock).limit(10).offset(0).all()

    for i in range(10):
        wishlist_query.add_stock_to_wishlist(
            db=db,
            current_user=reg1,
            wishlist_id=wishlist1.id,
            wishstock=schemas.WishStockCreate(
                stock_id=db_wishstock_list[i].id,
                purchase_price=db_wishstock_list[i].price,
                holding_num=i * 10,
            ),
        )

    # When
    stock_response = client.get(
        f"/wishlists/{wishlist1.id}/stocks",
        headers={"Authorization": "Bearer " + reg1_token},
    )

    # Then
    assert stock_response.status_code == 200
    assert len(stock_response.json()) == 10


def test_get_stock_in_wishlist():
    # Given
    db = TestingSessionLocal()
    reg1 = user_query.get_user_by_username(db=db, username="reg1")
    reg1_token = obtain_token_reg1()
    wishlist1 = get_wishlist_by_name(db=db, current_user=reg1, name="wishlist1")
    db_stock = db.query(models.Stock).filter(models.Stock.id == 1).first()

    wishlist_query.add_stock_to_wishlist(
        db=db,
        current_user=reg1,
        wishlist_id=wishlist1.id,
        wishstock=schemas.WishStockCreate(
            stock_id=db_stock.id,
            purchase_price="100000",
            holding_num=10,
        ),
    )

    # When
    stock_response = client.get(
        f"/wishlists/{wishlist1.id}/stocks/{db_stock.id}",
        headers={"Authorization": "Bearer " + reg1_token},
    )

    # Then
    assert stock_response.status_code == 200
    assert stock_response.json()["stock"]["name"] == db_stock.name


def test_update_stock_in_wishlist():
    # Given
    db = TestingSessionLocal()
    reg1 = user_query.get_user_by_username(db=db, username="reg1")
    reg1_token = obtain_token_reg1()
    wishlist1 = get_wishlist_by_name(db=db, current_user=reg1, name="wishlist1")

    db_stock = db.query(models.Stock).filter(models.Stock.id == 1).first()

    wishlist_query.add_stock_to_wishlist(
        db=db,
        current_user=reg1,
        wishlist_id=wishlist1.id,
        wishstock=schemas.WishStockCreate(
            stock_id=db_stock.id,
            purchase_price="100000",
            holding_num=10,
        ),
    )

    # When
    stock_response = client.put(
        f"/wishlists/{wishlist1.id}/stocks/{db_stock.id}",
        json={"purchase_price": 120000, "holding_num": 100},
        headers={"Authorization": "Bearer " + reg1_token},
    )

    # Then
    assert stock_response.status_code == 200
    assert stock_response.json()["purchase_price"] == 120000
    assert stock_response.json()["holding_num"] == 100


def test_delete_stock_in_wishlist():
    # Given
    db = TestingSessionLocal()
    reg1 = user_query.get_user_by_username(db=db, username="reg1")
    reg1_token = obtain_token_reg1()
    wishlist1 = get_wishlist_by_name(db=db, current_user=reg1, name="wishlist1")

    db_stock = db.query(models.Stock).filter(models.Stock.id == 1).first()

    wishlist_query.add_stock_to_wishlist(
        db=db,
        current_user=reg1,
        wishlist_id=wishlist1.id,
        wishstock=schemas.WishStockCreate(
            stock_id=db_stock.id,
            purchase_price="100000",
            holding_num=10,
        ),
    )

    # When
    stock_response = client.delete(
        f"/wishlists/{wishlist1.id}/stocks/{db_stock.id}",
        headers={"Authorization": "Bearer " + reg1_token},
    )

    deleted_wishstock_query_res = db.query(models.WishlistXstock).filter(
        models.WishlistXstock.wishlist_id == wishlist1.id,
        models.WishlistXstock.stock_id == db_stock.id,
    )

    # Then
    assert stock_response.status_code == 200
    assert deleted_wishstock_query_res.first() is None


def test_change_stock_order():
    # Given
    db = TestingSessionLocal()
    reg1 = user_query.get_user_by_username(db=db, username="reg1")
    reg1_token = obtain_token_reg1()
    wishlist1 = get_wishlist_by_name(db=db, current_user=reg1, name="wishlist1")

    db_stock_list = db.query(models.Stock).limit(10).offset(0).all()

    for i in range(10):
        wishlist_query.add_stock_to_wishlist(
            db=db,
            current_user=reg1,
            wishlist_id=wishlist1.id,
            wishstock=schemas.WishStockCreate(
                stock_id=db_stock_list[i].id,
                purchase_price=db_stock_list[i].price,
                holding_num=i * 10,
            ),
        )

    origin_order = 2
    hope_order = 5

    db_wishstock = (
        db.query(models.WishlistXstock)
        .filter(
            models.WishlistXstock.wishlist_id == wishlist1.id,
            models.WishlistXstock.order_num == origin_order,
        )
        .first()
    )

    # When
    stock_order_response = client.put(
        f"/wishlists/{wishlist1.id}/stocks/{db_wishstock.stock_id}/order",
        headers={"Authorization": "Bearer " + reg1_token},
        params={"hope_order": hope_order},
    )

    # Then
    assert stock_order_response.status_code == 200
    assert stock_order_response.json()["order_num"] == hope_order

    db_wishstock_list = (
        db.query(models.WishlistXstock)
        .filter(
            models.WishlistXstock.wishlist_id == wishlist1.id,
        )
        .order_by(models.WishlistXstock.order_num)
        .all()
    )
    for i, wishstock in enumerate(db_wishstock_list):

        if i < origin_order or i > hope_order:
            assert wishstock.stock_id == db_stock_list[i].id
        elif i == hope_order:
            assert wishstock.stock_id == db_stock_list[origin_order].id
        else:
            assert wishstock.stock_id == db_stock_list[i].id + 1
