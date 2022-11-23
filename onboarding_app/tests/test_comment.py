import pytest

from onboarding_app import models, schemas
from onboarding_app.queries import (
    comment as comment_query,
    user as user_query,
    wishlist as wishlist_query,
)
from onboarding_app.tests.conftest import client
from onboarding_app.tests.utils import get_wishlist_by_name

client.authenticate("reg1")


@pytest.fixture(autouse=True)
def make_dumy_data(db_session):
    _create_wishlist(db_session)
    _add_comments_in_wishlist(db_session)
    _add_replies_in_comment(db_session)


def _create_wishlist(db_session):
    reg = user_query.get_user_by_username(db=db_session, username="reg1")
    wishlist = schemas.WishlistCreate(
        name="wishlist1",
        description="wishlist1 description",
    )
    wishlist_query.create_wishlist(db=db_session, current_user=reg, wishlist=wishlist)


def _add_comments_in_wishlist(db_session):
    reg = user_query.get_user_by_username(db=db_session, username="reg1")
    wishlist = get_wishlist_by_name(db=db_session, current_user=reg, name="wishlist1")

    for i in range(10):
        comment_query.create_comment(
            db=db_session,
            current_user=reg,
            comment=schemas.CommentCreate(content=f"comment{i}"),
            wishlist_id=wishlist.id,
        )


def _add_replies_in_comment(db_session):
    reg = user_query.get_user_by_username(db=db_session, username="reg1")
    comment = (
        db_session.query(models.Comment)
        .filter(models.Comment.content == "comment1")
        .first()
    )

    for i in range(10):
        comment_query.create_comment(
            db=db_session,
            current_user=reg,
            comment=schemas.CommentCreate(content=f"replies{i}"),
            wishlist_id=comment.wishlist_id,
            parent_id=comment.id,
            is_reply=True,
        )


def test_to_create_comment(db_session):
    # Given
    reg = user_query.get_user_by_username(db=db_session, username="reg1")
    wishlist = get_wishlist_by_name(db=db_session, name="wishlist1", current_user=reg)

    # When
    comment_response = client.post(
        f"/wishlists/{wishlist.id}/comments",
        json={"content": "content1"},
    )

    # Then
    assert comment_response.status_code == 200
    assert comment_response.json()["content"] == "content1"
    assert comment_response.json()["parent_id"] is None
    assert comment_response.json()["is_reply"] is False


def test_to_fetch_comments(db_session):
    # Given
    reg = user_query.get_user_by_username(db=db_session, username="reg1")
    wishlist = get_wishlist_by_name(db=db_session, name="wishlist1", current_user=reg)

    # When
    comment_fetch_response = client.get(
        f"/wishlists/{wishlist.id}/comments",
    )

    # Then
    assert comment_fetch_response.status_code == 200
    assert len(comment_fetch_response.json()) == 10


def test_to_get_comment(db_session):
    # Given
    reg = user_query.get_user_by_username(db=db_session, username="reg1")
    wishlist1 = get_wishlist_by_name(db=db_session, name="wishlist1", current_user=reg)

    comment = (
        db_session.query(models.Comment)
        .filter(models.Comment.content == "comment1")
        .first()
    )
    # When
    comment_get_response = client.get(
        f"/wishlists/{wishlist1.id}/comments/{comment.id}",
    )

    # Then
    assert comment_get_response.status_code == 200
    assert comment_get_response.json()["content"] == "comment1"


def test_to_update_comment(db_session):
    # Given
    reg = user_query.get_user_by_username(db=db_session, username="reg1")
    wishlist = get_wishlist_by_name(db=db_session, name="wishlist1", current_user=reg)

    comment = (
        db_session.query(models.Comment)
        .filter(models.Comment.content == "comment1")
        .first()
    )

    # When
    update_response = client.put(
        f"/wishlists/{wishlist.id}/comments/{comment.id}",
        json={"content": "updated"},
    )

    # Then
    assert update_response.status_code == 200
    assert update_response.json()["content"] == "updated"


def test_to_delete_comment_from_other_wishlist(db_session):
    # Given
    reg = user_query.get_user_by_username(db=db_session, username="reg1")
    wishlist = get_wishlist_by_name(db=db_session, name="wishlist1", current_user=reg)

    comment = comment_query.create_comment(
        db=db_session,
        current_user=reg,
        comment=schemas.CommentCreate(content="comment written by reg2"),
        wishlist_id=wishlist.id,
    )

    # When
    delete_response = client.delete(
        f"/wishlists/{wishlist.id}/comments/{comment.id}",
    )

    deleted_comment = (
        db_session.query(models.Comment).filter(models.Comment.id == comment.id).first()
    )

    # Then
    assert delete_response.status_code == 200
    assert deleted_comment is None


def test_to_create_reply_to_comment(db_session):
    # Given
    reg = user_query.get_user_by_username(db=db_session, username="reg1")
    wishlist = get_wishlist_by_name(db=db_session, name="wishlist1", current_user=reg)

    comment = (
        db_session.query(models.Comment)
        .filter(models.Comment.content == "comment1")
        .first()
    )

    # When
    reply_response = client.post(
        f"/wishlists/{wishlist.id}/comments/{comment.id}/replies",
        json={"content": "reply"},
    )

    # Then
    assert reply_response.status_code == 200
    assert reply_response.json()["content"] == "reply"
    assert reply_response.json()["parent_id"] == comment.id
    assert reply_response.json()["is_reply"] is True


def test_to_fetch_replies(db_session):
    # Given
    reg = user_query.get_user_by_username(db=db_session, username="reg1")
    wishlist = get_wishlist_by_name(db=db_session, name="wishlist1", current_user=reg)

    comment = (
        db_session.query(models.Comment)
        .filter(models.Comment.content == "comment1")
        .first()
    )

    # When
    reply_fetch_response = client.get(
        f"/wishlists/{wishlist.id}/comments/{comment.id}/replies",
    )

    # Then
    assert reply_fetch_response.status_code == 200
    assert len(reply_fetch_response.json()) == 10


def test_to_fetch_history(db_session):
    # Given
    reg = user_query.get_user_by_username(db=db_session, username="reg1")
    wishlist = get_wishlist_by_name(db=db_session, name="wishlist1", current_user=reg)

    comment = (
        db_session.query(models.Comment)
        .filter(models.Comment.content == "comment1")
        .first()
    )

    for i in range(3):
        comment_query.update_comment(
            db=db_session,
            current_user=reg,
            comment=schemas.CommentCreate(content=f"updated {i}"),
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
    assert history_fetch_response.json()[0]["content"] == "updated 2"
