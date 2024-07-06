from enum import StrEnum
from pydantic import BaseModel


class ErrorCode(StrEnum):
    INCORRECT_CREDENTIALS = "INCORRECT_CREDENTIALS"
    INSUFFICIENT_PRIVILEGES = "INSUFFICIENT_PRIVILEGES"

    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"


class Error(BaseModel):
    error_code: ErrorCode
    user_feedback: str
