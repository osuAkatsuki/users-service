from pydantic import BaseModel
from app.common_types import UserPrivileges
import app.state


class User(BaseModel):
    id: int
    username: str
    privileges: UserPrivileges
    hashed_password: str


READ_PARAMS = """\
    id, username, privileges, password_md5
"""


async def fetch_one_by_username(username: str) -> User | None:
    query = f"""\
        SELECT {READ_PARAMS}
        FROM users
        WHERE username_safe = :username_safe
    """
    params = {"username_safe": username.lower().replace(" ", "_")}
    user = await app.state.database.fetch_one(query, params)
    if user is None:
        return None
    return User(
        id=user["id"],
        username=user["username"],
        privileges=UserPrivileges(user["privileges"]),
        hashed_password=user["password_md5"],
    )
