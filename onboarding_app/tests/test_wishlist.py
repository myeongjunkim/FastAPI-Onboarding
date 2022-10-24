from onboarding_app import models, schemas
from onboarding_app.queries import user as user_query, wishlist as wishlist_query
from onboarding_app.tests.conftest import client, TestingSessionLocal
from onboarding_app.tests.utils import get_wishlist_by_name, obtain_token_reg


def test_wishlists_create_success():
    # Given
    db = TestingSessionLocal()
    reg1_token = obtain_token_reg("reg1")
    reg1 = user_query.get_user_by_username(db=db, username="reg1")

    # When
    wishlist_response = client.post(
        "/wishlists",
        json={
            "name": "wishlist1",
            "description": "wishlist1 description",
        },
        headers={"Authorization": "Bearer " + reg1_token},
    )

    # Then
    assert wishlist_response.status_code == 200
    assert wishlist_response.json()["name"] == "wishlist1"
    assert wishlist_response.json()["description"] == "wishlist1 description"
    assert wishlist_response.json()["user_id"] == reg1.id


def test_wishlists_fetch_success():
    # Given
    reg1_token = obtain_token_reg("reg1")
    db = TestingSessionLocal()
    reg1 = user_query.get_user_by_username(db=TestingSessionLocal(), username="reg1")

    for i in range(10):
        wishlist_query.create_wishlist(
            db=db,
            current_user=reg1,
            wishlist=schemas.WishlistCreate(
                name=f"wishlist{i}",
                description=f"wishlist{i} description",
            ),
        )

    # When
    wishlists_response = client.get(
        "/wishlists",
        headers={"Authorization": "Bearer " + reg1_token},
    )

    # Then
    assert wishlists_response.status_code == 200
    assert len(wishlists_response.json()) == 10


def test_wishlists_get_success():
    # Given
    db = TestingSessionLocal()
    reg1_token = obtain_token_reg("reg1")
    reg1 = user_query.get_user_by_username(db=db, username="reg1")

    wishlist = wishlist_query.create_wishlist(
        db=db,
        current_user=reg1,
        wishlist=schemas.WishlistCreate(
            name="wishlist1",
            description="wishlist1 description",
        ),
    )

    # When
    wishlist_response_by_reg1 = client.get(
        f"/wishlists/{wishlist.id}",
        headers={"Authorization": "Bearer " + reg1_token},
    )

    # Then
    assert wishlist_response_by_reg1.status_code == 200
    assert wishlist_response_by_reg1.json()["name"] == "wishlist1"
    assert wishlist_response_by_reg1.json()["user_id"] == reg1.id


def test_wishlists_get_fail_with_other_user_token():
    # Given
    other_user_token = obtain_token_reg("reg2")

    db = TestingSessionLocal()
    reg1 = user_query.get_user_by_username(db=db, username="reg1")
    wishlist = wishlist_query.create_wishlist(
        db=db,
        current_user=reg1,
        wishlist=schemas.WishlistCreate(
            name="wishlist1",
            description="wishlist1 description",
        ),
    )

    # When
    wishlist_response_by_other_user = client.get(
        f"/wishlists/{wishlist.id}",
        headers={"Authorization": "Bearer " + other_user_token},
    )

    # Then
    assert wishlist_response_by_other_user.status_code == 401


def test_wishlists_update_success():
    # Given
    db = TestingSessionLocal()
    reg1_token = obtain_token_reg("reg1")
    reg1 = user_query.get_user_by_username(db=db, username="reg1")

    wishlist = wishlist_query.create_wishlist(
        db=db,
        current_user=reg1,
        wishlist=schemas.WishlistCreate(
            name="wishlist1",
            description="wishlist1 description",
        ),
    )

    # When
    wishlist_response_by_reg1 = client.put(
        f"/wishlists/{wishlist.id}",
        json={
            "name": "wishlist1 updated",
            "description": "wishlist1 description updated",
        },
        headers={"Authorization": "Bearer " + reg1_token},
    )

    # Then
    assert wishlist_response_by_reg1.status_code == 200
    assert wishlist_response_by_reg1.json()["name"] == "wishlist1 updated"
    assert (
        wishlist_response_by_reg1.json()["description"]
        == "wishlist1 description updated"
    )


def test_wishlists_delete_success():
    # Given
    db = TestingSessionLocal()
    reg1_token = obtain_token_reg("reg1")
    reg1 = user_query.get_user_by_username(db=db, username="reg1")

    wishlist = wishlist_query.create_wishlist(
        db=db,
        current_user=reg1,
        wishlist=schemas.WishlistCreate(
            name="wishlist1", description="wishlist1 description"
        ),
    )

    # When
    wishlist_response_by_reg1 = client.delete(
        f"/wishlists/{wishlist.id}",
        headers={"Authorization": "Bearer " + reg1_token},
    )

    wishlist_query_res = db.query(models.Wishlist).filter(
        models.Wishlist.id == wishlist.id
    )

    # Then
    assert wishlist_response_by_reg1.status_code == 200
    assert wishlist_query_res.first() is None


def test_wishlists_update_and_delete_fail_with_other_user_token():

    # Given
    other_user_token = obtain_token_reg("reg2")

    db = TestingSessionLocal()
    reg1 = user_query.get_user_by_username(db=db, username="reg1")
    wishlist = wishlist_query.create_wishlist(
        db=db,
        current_user=reg1,
        wishlist=schemas.WishlistCreate(
            name="wishlist1", description="wishlist1 description"
        ),
    )

    # When
    wishlist_update_response_by_other_uesr = client.put(
        f"/wishlists/{wishlist.id}",
        json={
            "name": "wishlist1 updated",
            "description": "wishlist1 description updated",
        },
        headers={"Authorization": "Bearer " + other_user_token},
    )

    wishlist_delete_response_by_other_uesr = client.delete(
        f"/wishlists/{wishlist.id}",
        headers={"Authorization": "Bearer " + other_user_token},
    )

    # Then
    assert wishlist_update_response_by_other_uesr.status_code == 401
    assert wishlist_delete_response_by_other_uesr.status_code == 401


def test_change_wishlist_order():
    # Given
    db = TestingSessionLocal()
    reg1_token = obtain_token_reg("reg1")
    reg1 = user_query.get_user_by_username(db=db, username="reg1")

    for i in range(10):
        wishlist_query.create_wishlist(
            db=db,
            current_user=reg1,
            wishlist=schemas.WishlistCreate(
                name=f"wishlist{i}",
                description=f"wishlist{i} description",
            ),
        )
    db_wishlist = get_wishlist_by_name(db=db, name="wishlist2", current_user=reg1)

    origin_order = 2
    hope_order = 5

    # When
    wishlist_order_response = client.put(
        f"/wishlists/{db_wishlist.id}/order",
        headers={"Authorization": "Bearer " + reg1_token},
        params={"hope_order": hope_order},
    )

    # Then
    assert wishlist_order_response.status_code == 200
    assert wishlist_order_response.json()["order_num"] == hope_order

    for i in range(10):
        db_wishlist = get_wishlist_by_name(
            db=db, name=f"wishlist{i}", current_user=reg1
        )
        if i < origin_order or i > hope_order:
            assert db_wishlist.order_num == i
        elif i == origin_order:
            assert db_wishlist.order_num == hope_order
        else:
            assert db_wishlist.order_num == i - 1
