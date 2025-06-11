from enum import StrEnum

from pydantic import BaseModel


class ErrorCode(StrEnum):
    INCORRECT_CREDENTIALS = "INCORRECT_CREDENTIALS"
    INSUFFICIENT_PRIVILEGES = "INSUFFICIENT_PRIVILEGES"
    PENDING_VERIFICATION = "PENDING_VERIFICATION"
    BAD_REQUEST = "BAD_REQUEST"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"

    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"


class Error(BaseModel):
    error_code: ErrorCode
    user_feedback: str
