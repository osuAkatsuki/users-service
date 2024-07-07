from fastapi import APIRouter
from fastapi import Response
from fastapi import Query

from app.api.responses import JSONResponse
from app.errors import Error
from app.errors import ErrorCode
from app.common_types import GameMode
from app.common_types import RelaxMode
from app.common_types import AkatsukiMode
from app.usecases import user_stats

router = APIRouter(tags=["(Public) User Stats API"])

def map_error_code_to_http_status_code(error_code: ErrorCode) -> int:
    return _error_code_to_http_status_code_map[error_code]


_error_code_to_http_status_code_map: dict[ErrorCode, int] = {
    ErrorCode.INCORRECT_CREDENTIALS: 401,
    ErrorCode.INSUFFICIENT_PRIVILEGES: 401,
    ErrorCode.PENDING_VERIFICATION: 401,
    ErrorCode.NOT_FOUND: 404,
    ErrorCode.INTERNAL_SERVER_ERROR: 500,
}

@router.get("/public/api/v1/users/{user_id}/stats")
async def get_user_stats(
    user_id: int,
    game_mode: GameMode = Query(...),
    relax_mode: RelaxMode = Query(...),
) -> Response:
    akatsuki_mode = AkatsukiMode.from_game_mode_and_relax_mode(game_mode, relax_mode)

    response = await user_stats.fetch_one_by_user_id_and_akatsuki_mode(user_id, akatsuki_mode)
    if isinstance(response, Error):
        return JSONResponse(
            content=response.model_dump(),
            status_code=map_error_code_to_http_status_code(response.error_code),
        )

    return JSONResponse(
        content=response.model_dump(),
        status_code=200,
    )

