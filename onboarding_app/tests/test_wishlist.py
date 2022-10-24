import pytest

from onboarding_app import models, schemas
from onboarding_app.queries import user as user_query, wishlist as wishlist_query
from onboarding_app.tests.conftest import client, TestingSessionLocal
from onboarding_app.tests.utils import get_wishlist_by_name, obtain_token_reg

db = TestingSessionLocal()


def test_wishlists_create_success():
    # Given
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


@pytest.mark.parametrize(
    "origin_order, hope_order",
    (
        # 범위 내에서 정렬
        (2, 7),  # Case 1. 낮은 순서에서 높은 순서로 올라가는 경우
        (5, 2),  # Case 2. 높은 순서에서 낮은 순서로 내려가는 경우
        (3, 3),  # Case 3. 같은 순서로 정렬하는 경우
    ),
)
def test_change_wishlist_order(origin_order: int, hope_order: int):
    # Given
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
    target_wishlist = get_wishlist_by_name(
        db=db, name=f"wishlist{origin_order}", current_user=reg1
    )

    # When
    wishlist_order_response = client.put(
        f"/wishlists/{target_wishlist.id}/order",
        headers={"Authorization": "Bearer " + reg1_token},
        params={"hope_order": hope_order},
    )

    # Then
    assert wishlist_order_response.status_code == 200
    assert wishlist_order_response.json()["order_num"] == hope_order

    wishlists_ordered_by_order_num = (
        db.query(models.Wishlist)
        .filter(
            models.Wishlist.user_id == reg1.id,
        )
        .order_by(models.Wishlist.order_num)
        .all()
    )

    for i, wishlist in enumerate(wishlists_ordered_by_order_num):

        if i < min(origin_order, hope_order) or i > max(origin_order, hope_order):
            assert wishlist.name == f"wishlist{i}"
        elif i == hope_order:
            assert wishlist.name == f"wishlist{origin_order}"
        else:
            gap = 1 if origin_order < hope_order else -1
            assert wishlist.name == f"wishlist{i + gap}"
