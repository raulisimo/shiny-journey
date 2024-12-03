from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from schemas.users import UserBase

# Mocked user roles and permissions for simplicity
fake_users_db = {
    "token123": UserBase(id=1, username="admin_user", roles=["admin"], is_active=True),
    "token456": UserBase(id=2, username="regular_user", roles=["user"], is_active=True),
}

# Headers: Authorization
# Value: Bearer <token>

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(token: str = Depends(oauth2_scheme)) -> UserBase:
    """
    Extract and validate the user from the token
    """
    user = fake_users_db.get(token)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user


def require_role(role: str):
    """
    Ensure the user has a specific role
    """

    def role_checker(user: UserBase = Depends(get_current_user)):
        if role not in user.roles:
            raise HTTPException(status_code=403, detail="Forbidden: Insufficient permissions")
        return user

    return role_checker
