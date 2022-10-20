import pytest

from onboarding_app import models, schemas
from onboarding_app.queries import (
    comment as comment_query,
    user as user_query,
    wishlist as wishlist_query,
)
from onboarding_app.tests.conftest import client, engine, TestingSessionLocal
from onboarding_app.tests.utils import (
    get_wishlist_by_name,
    obtain_token_reg1,
    obtain_token_reg2,
)
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
    assert comment_response.json()["parent_id"] is None
    assert comment_response.json()["is_reply"] is False


def test_fetch_comments():
    # Given
    db = TestingSessionLocal()
    reg1 = user_query.get_user_by_username(db=db, username="reg1")
    reg2 = user_query.get_user_by_username(db=db, username="reg2")
    register_list = [reg1, reg2]
    wishlist1 = get_wishlist_by_name(db=db, name="wishlist1", current_user=reg1)

    for i in range(10):
        comment_query.create_comment(
            db=db,
            current_user=register_list[i % 2],
            comment=schemas.CommentCreate(body=f"comment{i}"),
            wishlist_id=wishlist1.id,
        )

    # When
    comment_fetch_response = client.get(
        f"/wishlists/{wishlist1.id}/comments",
    )

    # Then
    assert comment_fetch_response.status_code == 200
    assert len(comment_fetch_response.json()) == 10


def test_create_reply_to_comment():
    # Given
    db = TestingSessionLocal()
    reg1_token = obtain_token_reg1()
    reg1 = user_query.get_user_by_username(db=db, username="reg1")
    wishlist1 = get_wishlist_by_name(db=db, name="wishlist1", current_user=reg1)

    comment1 = comment_query.create_comment(
        db=db,
        current_user=reg1,
        comment=schemas.CommentCreate(body="body1"),
        wishlist_id=wishlist1.id,
    )

    # When
    reply_response = client.post(
        f"/wishlists/{wishlist1.id}/comments/{comment1.id}",
        json={"body": "reply"},
        headers={"Authorization": "Bearer " + reg1_token},
    )

    # Then
    assert reply_response.status_code == 200
    assert reply_response.json()["body"] == "reply"
    assert reply_response.json()["parent_id"] == comment1.id
    assert reply_response.json()["is_reply"] is True


def test_update_comment():
    # Given
    db = TestingSessionLocal()
    reg2_token = obtain_token_reg2()
    reg1 = user_query.get_user_by_username(db=db, username="reg1")
    reg2 = user_query.get_user_by_username(db=db, username="reg2")
    wishlist1 = get_wishlist_by_name(db=db, name="wishlist1", current_user=reg1)

    reg2_comment = comment_query.create_comment(
        db=db,
        current_user=reg2,
        comment=schemas.CommentCreate(body="comment written by reg2"),
        wishlist_id=wishlist1.id,
    )

    # When
    update_response = client.put(
        f"/wishlists/{wishlist1.id}/comments/{reg2_comment.id}",
        json={"body": "updated by reg2"},
        headers={"Authorization": "Bearer " + reg2_token},
    )

    # Then
    assert update_response.status_code == 200
    assert update_response.json()["body"] == "updated by reg2"


def test_delete_comment():
    # Given
    db = TestingSessionLocal()
    reg2_token = obtain_token_reg2()
    reg1 = user_query.get_user_by_username(db=db, username="reg1")
    reg2 = user_query.get_user_by_username(db=db, username="reg2")
    wishlist1 = get_wishlist_by_name(db=db, name="wishlist1", current_user=reg1)

    reg2_comment = comment_query.create_comment(
        db=db,
        current_user=reg2,
        comment=schemas.CommentCreate(body="comment written by reg2"),
        wishlist_id=wishlist1.id,
    )

    # When
    delete_response = client.delete(
        f"/wishlists/{wishlist1.id}/comments/{reg2_comment.id}",
        headers={"Authorization": "Bearer " + reg2_token},
    )

    deleted_comment = (
        db.query(models.Comment).filter(models.Comment.id == reg2_comment.id).first()
    )

    # Then
    assert delete_response.status_code == 200
    assert deleted_comment is None
