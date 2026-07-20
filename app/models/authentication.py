from datetime import datetime

from pydantic import BaseModel

from app.common_types import UserPrivileges


class Identity(BaseModel):
    user_id: int
    username: str
    privileges: UserPrivileges


class AuthorizationGrant(BaseModel):
    unhashed_access_token: str
    identity: Identity
    privileges: UserPrivileges
    expires_at: datetime | None
