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


def generate_unhashed_secure_token() -> str:
    return secrets.token_urlsafe(nbytes=32)


def hash_secure_token(unhashed_secure_token: str) -> str:
    return hashlib.md5(
        unhashed_secure_token.encode(),
        usedforsecurity=False,
    ).hexdigest()


def validate_password_meets_requirements(password: str, /) -> bool:
    """
    Validates that the password meets the security requirements.
    - Must be at least 8 characters long
    - Must contain at least one digit
    - Must contain at least one uppercase letter
    - Must contain at least one lowercase letter
    """
    if len(password) < 8:
        return False
    if not any(char.isdigit() for char in password):
        return False
    if not any(char.isupper() for char in password):
        return False
    if not any(char.islower() for char in password):
        return False
    return True
