from fastapi import APIRouter
from fastapi import Response
from fastapi.responses import JSONResponse

from app.usecases import user_stats
from app.usecases import users

router = APIRouter(tags=["(Public) Overall Stats API"])


@router.get("/public/api/v1/overall-stats/total-registered-users")
async def fetch_total_registered_user_count() -> Response:
    response = await users.fetch_total_registered_user_count()
    return JSONResponse(
        content=response,
        status_code=200,
    )


@router.get("/public/api/v1/overall-stats/total-pp-earned")
async def get_global_total_pp_earned() -> Response:
    response = await user_stats.fetch_global_total_pp_earned()
    return JSONResponse(
        content=response,
        status_code=200,
    )
