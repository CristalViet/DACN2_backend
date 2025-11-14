from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config import SECRET_KEY
from app.core.security import ALGORITHM
from app.database import get_db
from app import models
from typing import Any

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Any:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.get(models.user.User, int(user_id))
    if user is None:
        raise credentials_exception
    return user


def require_admin(current_user = Depends(get_current_user)):
    """Require user to have admin role"""
    if not current_user.role or current_user.role.role_name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def require_writer(current_user = Depends(get_current_user)):
    """Require user to have writer role"""
    if not current_user.role or current_user.role.role_name not in ["writer", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Writer or Admin access required"
        )
    return current_user


