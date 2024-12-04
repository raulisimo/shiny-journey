import pytest
from fastapi import FastAPI, Depends
from fastapi.exceptions import HTTPException
from fastapi.testclient import TestClient

from dependencies.authorization import require_role, get_current_user
from schemas.users import UserBase

app = FastAPI()


# Sample endpoint to test `require_role`
@app.get("/admin-only")
def admin_only(user: UserBase = Depends(require_role("admin"))):
    return {"message": f"Welcome, {user.username}"}


# Test client
client = TestClient(app)


def test_get_current_user_valid_token():
    token = "token123"
    user = get_current_user(token=token)
    assert user.username == "admin_user"
    assert user.roles == ["admin"]


def test_get_current_user_invalid_token():
    with pytest.raises(HTTPException) as excinfo:
        get_current_user(token="invalid_token")
    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "Unauthorized"


def test_get_current_user_inactive_user():
    fake_users_db = {
        "token789": UserBase(id=3, username="inactive_user", roles=["user"], is_active=False),
    }
    with pytest.raises(HTTPException) as excinfo:
        get_current_user(token="token789")
    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "Unauthorized"


def test_require_role_valid():
    token = "token123"
    user = get_current_user(token=token)
    role_checker = require_role("admin")
    result = role_checker(user=user)
    assert result == user


def test_require_role_invalid():
    token = "token456"  # Regular user token
    user = get_current_user(token=token)
    role_checker = require_role("admin")
    with pytest.raises(HTTPException) as excinfo:
        role_checker(user=user)
    assert excinfo.value.status_code == 403
    assert excinfo.value.detail == "Forbidden: Insufficient permissions"


def test_admin_only_endpoint_valid():
    response = client.get("/admin-only", headers={"Authorization": "Bearer token123"})
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome, admin_user"}


def test_admin_only_endpoint_forbidden():
    response = client.get("/admin-only", headers={"Authorization": "Bearer token456"})
    assert response.status_code == 403
    assert response.json() == {"detail": "Forbidden: Insufficient permissions"}


def test_admin_only_endpoint_unauthorized():
    response = client.get("/admin-only", headers={"Authorization": "Bearer invalid_token"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Unauthorized"}
