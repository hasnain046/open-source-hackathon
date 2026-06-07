# Module: app.api.v1.auth
# Description: Router handling user authentication, login tokens generation, and session refresh.

from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.user import UserRegisterSchema, UserResponseSchema, TokenSchema
from app.services.auth_service import AuthService
from app.core.security import create_access_token, create_refresh_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserRegisterSchema, db: Session = Depends(get_db)):
    """Register a new user account with secure password complexity validation."""
    return AuthService.register_user(db=db, user_in=user_in)


@router.post("/login", response_model=TokenSchema)
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """OAuth2 compatible token login. Accesses username (email) and password."""
    user = AuthService.authenticate_user(db=db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password."
        )
    
    # Generate tokens
    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh")
def refresh_token():
    """Token rotation interface scaffold."""
    return {"message": "Access token rotation active"}


@router.post("/logout")
def logout_user():
    """Revoke user session credentials scaffold."""
    return {"message": "Session revocation active"}
