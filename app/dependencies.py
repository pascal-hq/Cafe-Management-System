# app/dependencies.py

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from .database import SessionLocal
from .models import User
from .auth import SECRET_KEY, ALGORITHM

# ===============================
# OAuth2 JWT scheme
# auto_error=False allows guests to access public endpoints
# ===============================
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


# ===============================
# DATABASE SESSION DEPENDENCY
# ===============================
def get_db() -> Session:
    """
    Provides a SQLAlchemy DB session and ensures cleanup after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ===============================
# STRICT AUTH: Admin / Staff Only
# ===============================
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Strict authentication.
    Raises 401 if token is missing, invalid, or user not found.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token missing",
            headers={"WWW-Authenticate": "Bearer"},
        )

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        if not username:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise credentials_exception

    return user


# ===============================
# OPTIONAL AUTH: Guests Allowed
# ===============================
def get_optional_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Returns a User object if JWT token is valid.
    Returns None if token is missing or invalid (guest access).
    """
    if not token:
        return None

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: Optional[str] = payload.get("sub")
        if not username:
            return None
    except JWTError:
        return None

    return db.query(User).filter(User.username == username).first()


# ===============================
# ROLE-BASED ACCESS CONTROL
# ===============================
def require_role(required_role: str):
    """
    Enforce role-based access for endpoints.

    Usage:
        @router.post("/", dependencies=[Depends(require_role("admin"))])
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User must have '{required_role}' role"
            )
        return current_user

    return role_checker
