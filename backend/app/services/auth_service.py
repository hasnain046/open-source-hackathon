# Module: app.services.auth_service
# Description: Service handling user registration, credentials authentication, and token generation operations.

from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.schemas.user import UserRegisterSchema
from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token


class AuthService:
    @staticmethod
    def register_user(db: Session, user_in: UserRegisterSchema) -> User:
        """Create a new user in the database after checking if the email is already registered."""
        existing_user = db.query(User).filter(User.email == user_in.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The email is already registered in the system."
            )
        
        # Hash the plain password
        hashed_password = get_password_hash(user_in.password)
        
        # Create user record
        db_user = User(
            email=user_in.email,
            password_hash=hashed_password,
            full_name=user_in.full_name,
            role=user_in.role
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate user credentials using email and verify password hash."""
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user
