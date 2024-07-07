from enum import StrEnum

from pydantic import BaseModel


class ErrorCode(StrEnum):
    INCORRECT_CREDENTIALS = "INCORRECT_CREDENTIALS"
    INSUFFICIENT_PRIVILEGES = "INSUFFICIENT_PRIVILEGES"
    PENDING_VERIFICATION = "PENDING_VERIFICATION"
    NOT_FOUND = "NOT_FOUND"

    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"


class Error(BaseModel):
    error_code: ErrorCode
    user_feedback: str

def map_error_code_to_http_status_code(error_code: ErrorCode) -> int:
    return _error_code_to_http_status_code_map[error_code]

_error_code_to_http_status_code_map: dict[ErrorCode, int] = {
    ErrorCode.INCORRECT_CREDENTIALS: 401,
    ErrorCode.INSUFFICIENT_PRIVILEGES: 401,
    ErrorCode.PENDING_VERIFICATION: 401,
    ErrorCode.NOT_FOUND: 404,
    ErrorCode.INTERNAL_SERVER_ERROR: 500,
}