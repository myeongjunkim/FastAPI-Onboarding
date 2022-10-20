import pytest

from onboarding_app import schemas
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


def test_create_comment():
    # Given
    db = TestingSessionLocal()
    reg1_token = obtain_token_reg1()
    reg1 = user_query.get_user_by_username(db=db, username="reg1")
    wishlist1 = get_wishlist_by_name(db=db, name="wishlist1", current_user=reg1)

    # When
    comment_response = client.post(
        f"/wishlists/{wishlist1.id}/comments",
        json={"body": "body1"},
        headers={"Authorization": "Bearer " + reg1_token},
    )

    # Then
    assert comment_response.status_code == 200
    assert comment_response.json()["body"] == "body1"
