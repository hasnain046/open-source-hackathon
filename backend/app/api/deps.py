# Module: app.api.deps
# Description: Global dependencies for database session injections and OAuth2 user credential roles validation.

from typing import Generator, List
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.core.database import SessionLocal
from app.core.exceptions import CredentialsException, PermissionDeniedException

from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)


def get_db() -> Generator[Session, None, None]:
    """Provide local request database session scope."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """Validate JWT signature, query database, and return active User entity."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        if user_id is None or token_type != "access":
            raise CredentialsException()
    except jwt.PyJWTError:
        raise CredentialsException()

    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise CredentialsException("User account is inactive or not found.")
    return user


class RoleChecker:
    """FastAPI role authorization filter dependency."""
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        """Verify logged-in user belongs to allowed role brackets."""
        if current_user.role not in self.allowed_roles:
            raise PermissionDeniedException("Role authorization failed.")
        return current_user
