from fastapi import APIRouter
from fastapi import Response
from fastapi import Path

from app.api.responses import JSONResponse
from app.usecases import users
from app.errors import Error
from app.errors import map_error_code_to_http_status_code

router = APIRouter(tags=["(Public) Users API"])

@router.get("/public/api/v1/users/{user_id}")
async def get_user(
    user_id: int = Path(...)
) -> Response:
    response = await users.fetch_one_by_user_id(user_id)
    if isinstance(response, Error):
        return JSONResponse(
            content=response.model_dump(),
            status_code=map_error_code_to_http_status_code(response.error_code),
        )
    
    return JSONResponse(
        content=response.model_dump(),
        status_code=200,
    )
