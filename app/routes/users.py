# app/routes/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app import models, schemas, auth
from app.database import SessionLocal

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -----------------------------
# Login route (OAuth2 password flow)
# -----------------------------
@router.post("/login", response_model=schemas.Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # Check if user exists
    db_user = db.query(models.User).filter(
        models.User.username == form_data.username
    ).first()

    # Verify password
    if not db_user or not auth.verify_password(form_data.password, db_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create JWT token
    access_token = auth.create_access_token(
        data={
            "sub": db_user.username,
            "role": db_user.role
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
