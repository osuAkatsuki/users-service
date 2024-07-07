from fastapi import APIRouter

from . import authentication
from . import users

public_router = APIRouter()

public_router.include_router(authentication.router)
public_router.include_router(users.router)