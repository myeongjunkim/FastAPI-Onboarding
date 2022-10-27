import pytest

from onboarding_app import models, schemas
from onboarding_app.queries import (
    comment as comment_query,
    user as user_query,
    wishlist as wishlist_query,
)
from onboarding_app.tests.conftest import client, TestingSessionLocal
from onboarding_app.tests.utils import get_wishlist_by_name, obtain_token_reg

db = TestingSessionLocal()


@pytest.fixture(autouse=True)
def make_dumy_data():
    _create_wishlist()
    _add_comments_in_wishlist()
    _add_replies_in_comment()


def _create_wishlist():
    reg = user_query.get_user_by_username(db=db, username="reg1")
    wishlist = schemas.WishlistCreate(
        name="wishlist1",
        description="wishlist1 description",
    )
    wishlist_query.create_wishlist(db=db, current_user=reg, wishlist=wishlist)


def _add_comments_in_wishlist():
    reg = user_query.get_user_by_username(db=db, username="reg1")
    wishlist = get_wishlist_by_name(db=db, current_user=reg, name="wishlist1")

    for i in range(10):
        comment_query.create_comment(
            db=db,
            current_user=reg,
            comment=schemas.CommentCreate(body=f"comment{i}"),
            wishlist_id=wishlist.id,
        )


def _add_replies_in_comment():
    reg = user_query.get_user_by_username(db=db, username="reg1")
    comment = db.query(models.Comment).filter(models.Comment.body == "comment1").first()

    for i in range(10):
        comment_query.create_comment(
            db=db,
            current_user=reg,
            comment=schemas.CommentCreate(body=f"replies{i}"),
            wishlist_id=comment.wishlist_id,
            parent_id=comment.id,
            is_reply=True,
        )


def test_to_create_comment():
    # Given
    db = TestingSessionLocal()
    reg_token = obtain_token_reg("reg1")
    reg = user_query.get_user_by_username(db=db, username="reg1")
    wishlist = get_wishlist_by_name(db=db, name="wishlist1", current_user=reg)

    # When
    comment_response = client.post(
        f"/wishlists/{wishlist.id}/comments",
        json={"body": "body1"},
        headers={"Authorization": "Bearer " + reg_token},
    )

    # Then
    assert comment_response.status_code == 200
    assert comment_response.json()["body"] == "body1"
    assert comment_response.json()["parent_id"] is None
    assert comment_response.json()["is_reply"] is False


def test_to_fetch_comments():
    # Given
    reg = user_query.get_user_by_username(db=db, username="reg1")
    wishlist = get_wishlist_by_name(db=db, name="wishlist1", current_user=reg)

    # When
    comment_fetch_response = client.get(
        f"/wishlists/{wishlist.id}/comments",
    )

    # Then
    assert comment_fetch_response.status_code == 200
    assert len(comment_fetch_response.json()) == 10


def test_to_get_comment():
    # Given
    reg = user_query.get_user_by_username(db=db, username="reg1")
    wishlist1 = get_wishlist_by_name(db=db, name="wishlist1", current_user=reg)

    comment = db.query(models.Comment).filter(models.Comment.body == "comment1").first()
    # When
    comment_get_response = client.get(
        f"/wishlists/{wishlist1.id}/comments/{comment.id}",
    )

    # Then
    assert comment_get_response.status_code == 200
    assert comment_get_response.json()["body"] == "comment1"


def test_to_update_comment():
    # Given
    reg_token = obtain_token_reg("reg1")
    reg = user_query.get_user_by_username(db=db, username="reg1")
    wishlist = get_wishlist_by_name(db=db, name="wishlist1", current_user=reg)

    comment = db.query(models.Comment).filter(models.Comment.body == "comment1").first()

    # When
    update_response = client.put(
        f"/wishlists/{wishlist.id}/comments/{comment.id}",
        json={"body": "updated"},
        headers={"Authorization": "Bearer " + reg_token},
    )

    # Then
    assert update_response.status_code == 200
    assert update_response.json()["body"] == "updated"


def test_to_delete_comment_from_other_wishlist():
    # Given
    reg2_token = obtain_token_reg("reg2")
    reg1 = user_query.get_user_by_username(db=db, username="reg1")
    reg2 = user_query.get_user_by_username(db=db, username="reg2")
    reg1_wishlist = get_wishlist_by_name(db=db, name="wishlist1", current_user=reg1)

    reg2_comment = comment_query.create_comment(
        db=db,
        current_user=reg2,
        comment=schemas.CommentCreate(body="comment written by reg2"),
        wishlist_id=reg1_wishlist.id,
    )

    # When
    delete_response = client.delete(
        f"/wishlists/{reg1_wishlist.id}/comments/{reg2_comment.id}",
        headers={"Authorization": "Bearer " + reg2_token},
    )

    deleted_comment = (
        db.query(models.Comment).filter(models.Comment.id == reg2_comment.id).first()
    )

    # Then
    assert delete_response.status_code == 200
    assert deleted_comment is None


def test_to_create_reply_to_comment():
    # Given
    reg_token = obtain_token_reg("reg1")
    reg = user_query.get_user_by_username(db=db, username="reg1")
    wishlist = get_wishlist_by_name(db=db, name="wishlist1", current_user=reg)

    comment = db.query(models.Comment).filter(models.Comment.body == "comment1").first()

    # When
    reply_response = client.post(
        f"/wishlists/{wishlist.id}/comments/{comment.id}/replies",
        json={"body": "reply"},
        headers={"Authorization": "Bearer " + reg_token},
    )

    # Then
    assert reply_response.status_code == 200
    assert reply_response.json()["body"] == "reply"
    assert reply_response.json()["parent_id"] == comment.id
    assert reply_response.json()["is_reply"] is True


def test_to_fetch_replies():
    # Given
    reg = user_query.get_user_by_username(db=db, username="reg1")
    wishlist = get_wishlist_by_name(db=db, name="wishlist1", current_user=reg)

    comment = db.query(models.Comment).filter(models.Comment.body == "comment1").first()

    # When
    reply_fetch_response = client.get(
        f"/wishlists/{wishlist.id}/comments/{comment.id}/replies",
    )

    # Then
    assert reply_fetch_response.status_code == 200
    assert len(reply_fetch_response.json()) == 10


def test_to_fetch_history():
    # Given
    reg = user_query.get_user_by_username(db=db, username="reg1")
    wishlist = get_wishlist_by_name(db=db, name="wishlist1", current_user=reg)

    comment = db.query(models.Comment).filter(models.Comment.body == "comment1").first()

    for i in range(3):
        comment_query.update_comment(
            db=db,
            current_user=reg,
            comment=schemas.CommentCreate(body=f"updated {i}"),
            wishlist_id=wishlist.id,
            comment_id=comment.id,
        )

    # When
    history_fetch_response = client.get(
        f"/wishlists/{wishlist.id}/comments/{comment.id}/history",
    )

    # Then
    assert history_fetch_response.status_code == 200
    assert len(history_fetch_response.json()) == 4
    assert history_fetch_response.json()[0]["body"] == "updated 2"
