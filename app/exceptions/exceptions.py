from fastapi import HTTPException, Response


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


class SuccessReposne(Response):
    def __init__(self, content = {"success": "ok"}, status_code = 200, headers = None, media_type = None, background = None):
        super().__init__(content, status_code, headers, media_type, background)