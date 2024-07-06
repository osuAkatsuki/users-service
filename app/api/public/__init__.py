from fastapi import APIRouter

from . import authentication

public_router = APIRouter()

public_router.include_router(authentication.router)
