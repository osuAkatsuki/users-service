import hashlib
import secrets

import bcrypt


def hash_osu_password(password: str) -> str:
    return bcrypt.hashpw(
        hashlib.md5(password.encode()).hexdigest().encode(),
        bcrypt.gensalt(),
    ).decode()


def check_osu_password(*, untrusted_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        hashlib.md5(untrusted_password.encode()).hexdigest().encode(),
        hashed_password.encode(),
    )


def generate_access_token() -> str:
    return secrets.token_urlsafe(32)
