# Module: app.api.v1.profile
# Description: Router handling user profile metadata and sandbox developer credentials tokens.

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.schemas.user import UserResponseSchema, ProfileUpdateSchema
from app.models.user import User
from app.core.security import get_password_hash

router = APIRouter(prefix="/profile", tags=["User Profile"])


@router.get("/me", response_model=UserResponseSchema)
def get_user_profile(current_user: User = Depends(get_current_user)):
    """Retrieve logged-in user profile attributes."""
    return current_user


@router.put("/update", response_model=UserResponseSchema)
def update_profile(
    payload: ProfileUpdateSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update profile details for the authenticated user."""
    if payload.email and payload.email != current_user.email:
        existing = db.query(User).filter(User.email == payload.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use."
            )
        current_user.email = payload.email

    if payload.full_name is not None:
        current_user.full_name = payload.full_name

    if payload.password is not None:
        current_user.password_hash = get_password_hash(payload.password)

    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/token")
def generate_developer_token(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Generate or rotate analyst developer sandbox access tokens."""
    # Simple mock token generation
    import secrets
    token = f"iq_sandbox_{secrets.token_hex(24)}"
    current_user.api_token = token
    db.add(current_user)
    db.commit()
    return {"message": "Sandbox credentials token successfully generated", "api_token": token}
