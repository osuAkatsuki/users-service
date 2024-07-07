from fastapi import APIRouter

from . import authentication
from . import users
from . import user_stats

public_router = APIRouter()

public_router.include_router(authentication.router)
public_router.include_router(users.router)
public_router.include_router(user_stats.router)
