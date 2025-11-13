from typing import Any, Mapping
import uuid
from fastapi import HTTPException, Response
from fastapi.responses import JSONResponse
from starlette.background import BackgroundTask

from app.models.base import Base


class ErrorRolePermissionDenied(HTTPException):
    def __init__(
        self,
        required_role: str,
        actual_role: str|None = None,
        status_code: int = 403,
        detail: str|None = None
    ):
        if detail is None:
            detail = (
                f"Access denied: required role '{required_role}', "
                f"got '{actual_role}'"
            )
        super().__init__(status_code=status_code, detail=detail)

class ErrorPermissionDenied(HTTPException):
    def __init__(
        self,
        status_code: int = 403,
        detail: str|None = None
    ):
        if detail is None:
            detail = (
                "This user haven't permission to make this"
            )
        super().__init__(status_code=status_code, detail=detail)


class ErrorAlreadyExists(HTTPException):
    def __init__(
        self,
        entity: Base,
        status_code: int = 409,
        detail = None,
    ):
        if detail is None:
            detail = (
                f"{entity.__name__[0:-1]}, already exists"
            )
        super().__init__(status_code=status_code, detail=detail)

class ErrorNotExists(HTTPException):
    def __init__(
        self,
        entity: Base,
        status_code: int = 404,
        detail = None,
    ):
        if detail is None:
            detail = (
                f"This {entity.__name__[0:-1]}, not exists"
            )
        super().__init__(status_code=status_code, detail=detail)


class Success(JSONResponse):
    def __init__(self, content: Any = {"status": "ok"}, status_code: int = 200, headers: Mapping[str, str] | None = None, media_type: str | None = None, background: BackgroundTask | None = None) -> None:
        super().__init__(content, status_code, headers, media_type, background)