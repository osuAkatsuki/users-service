import hashlib
import secrets

import bcrypt


def hash_osu_password(password: str) -> str:
    return bcrypt.hashpw(
        password=hashlib.md5(
            password.encode(),
            usedforsecurity=False,
        )
        .hexdigest()
        .encode(),
        salt=bcrypt.gensalt(),
    ).decode()


def check_osu_password(
    *,
    untrusted_password: str,
    hashed_password: str,
) -> bool:
    return bcrypt.checkpw(
        password=hashlib.md5(
            untrusted_password.encode(),
            usedforsecurity=False,
        )
        .hexdigest()
        .encode(),
        hashed_password=hashed_password.encode(),
    )


def generate_unhashed_access_token() -> str:
    return secrets.token_urlsafe(nbytes=32)


def hash_access_token(unhashed_access_token: str) -> str:
    return hashlib.md5(
        unhashed_access_token.encode(),
        usedforsecurity=False,
    ).hexdigest()
