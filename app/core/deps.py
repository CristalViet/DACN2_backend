from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session, selectinload

from app.config import SECRET_KEY
from app.core.security import ALGORITHM
from app.database import get_db
from app import models
from typing import Any

security = HTTPBearer()

def get_current_user(
    # 2. Change the type hint and variable name to avoid confusion
    auth: HTTPAuthorizationCredentials = Depends(security), 
    db: Session = Depends(get_db)
) -> Any:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # 3. EXTRACT THE TOKEN STRING HERE
    token = auth.credentials 

    try:
        # Now 'token' is a string, so jwt.decode will work
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    # Eager load role relationship using selectinload (better for async contexts)
    user = db.query(models.user.User).options(
        selectinload(models.user.User.role)
    ).filter(models.user.User.id == int(user_id)).first()
    
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


