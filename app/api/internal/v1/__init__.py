from fastapi import APIRouter

from app.api.internal.v1 import users

v1_router = APIRouter()

v1_router.include_router(users.router)
