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

    # When
    stock_response = client.post(
        f"/wishlists/{wishlist1.id}/stocks",
        json={"stock_name": "카카오", "purchase_price": 12332, "holding_num": 10},
        headers={"Authorization": "Bearer " + reg1_token},
    )

    # Then
    assert stock_response.status_code == 200
    assert stock_response.json()["stock_name"] == "카카오"


def test_fetch_stock_in_wishlist():
    # Given
    db = TestingSessionLocal()
    reg1 = user_query.get_user_by_username(db=db, username="reg1")
    reg1_token = obtain_token_reg1()
    wishlist1 = get_wishlist_by_name(db=db, current_user=reg1, name="wishlist1")

    dbstock_list = db.query(models.Stock).limit(10).offset(0).all()
    print(len(dbstock_list))

    for i in range(10):
        wishlist_query.add_stock_to_wishlist(
            db=db,
            current_user=reg1,
            wishlist_id=wishlist1.id,
            wishlistXstock=schemas.WishStockCreate(
                stock_name=dbstock_list[i].name,
                purchase_price=dbstock_list[i].price,
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
