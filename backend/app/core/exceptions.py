# Module: app.core.exceptions
# Description: Global exception overrides and custom HTTP errors mappings.

from fastapi import HTTPException, status


class CredentialsException(HTTPException):
    """Exception raised when JWT validation fails."""
    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class PermissionDeniedException(HTTPException):
    """Exception raised when user lacks required role authorization."""
    def __init__(self, detail: str = "Not enough permissions to perform action"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )


class ResourceNotFoundException(HTTPException):
    """Exception raised when queried database item does not exist."""
    def __init__(self, detail: str = "Requested resource not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )
