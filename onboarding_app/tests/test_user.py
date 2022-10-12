from onboarding_app.queries import user as user_query
from onboarding_app.tests.conftest import client, TestingSessionLocal
from onboarding_app.tests.utils import obtain_token_admin, obtain_token_reg1


def test_signup_success():
    # When
    signup_response = client.post(
        "/users/signup",
        json={
            "username": "reg3",
            "email": "reg3@example.com",
            "password1": "reg3",
            "password2": "reg3",
        },
    )

    # Then
    assert signup_response.status_code == 200
    assert signup_response.json()["username"] == "reg3"


def test_login_success():
    # When
    response_token = client.post(
        "/users/token",
        data={
            "username": "admin",
            "password": "admin",
        },
        headers={"content-type": "application/x-www-form-urlencoded"},
    )

    # Then
    assert response_token.status_code == 200
    assert response_token.json() is not None


def test_only_admin_can_fetch_users():
    # Given
    admin_token = obtain_token_admin()
    user_token = obtain_token_reg1()

    # When
    response_users_by_admin = client.get(
        "/users",
        headers={"Authorization": "Bearer " + admin_token},
    )
    response_users_by_reg1 = client.get(
        "/users",
        headers={"Authorization": "Bearer " + user_token},
    )

    # Then
    assert response_users_by_admin.status_code == 200
    assert len(response_users_by_admin.json()) == 3
    assert response_users_by_reg1.status_code == 401


def test_only_admin_can_get_user():
    # Given
    admin_token = obtain_token_admin()
    user_token = obtain_token_reg1()
    check_user = user_query.get_user_by_username(
        db=TestingSessionLocal(), username="reg1"
    )

    # When
    response_by_admin = client.get(
        "/users/" + str(check_user.id),
        headers={"Authorization": "Bearer " + admin_token},
    )
    response_by_reg1 = client.get(
        "/users/" + str(check_user.id),
        headers={"Authorization": "Bearer " + user_token},
    )

    # Then
    assert response_by_admin.status_code == 200
    assert response_by_admin.json()["username"] == "reg1"
    assert response_by_reg1.status_code == 401
