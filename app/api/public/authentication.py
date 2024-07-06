from fastapi import APIRouter
from fastapi import Header
from fastapi import Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.errors import Error
from app.usecases import authentication

router = APIRouter(tags=["(Public) Web Authentication API"])


class AuthenticationRequest(BaseModel):
    username: str
    password: str


@router.post("/public/api/v1/authenticate")
async def authenticate(
    args: AuthenticationRequest,
    client_ip_address: str = Header(..., alias="X-Real-IP"),
    client_user_agent: str = Header(..., alias="User-Agent"),
) -> Response:
    response = await authentication.authenticate(
        username=args.username,
        password=args.password,
        client_ip_address=client_ip_address,
        client_user_agent=client_user_agent,
    )
    if isinstance(response, Error):
        return JSONResponse(content=response.model_dump(), status_code=401)

    http_response = JSONResponse(
        content=response.identity.model_dump(),
        status_code=200,
    )
    http_response.set_cookie(
        "X-Akatsuki-Access-Token",
        value=response.access_token,
        domain="akatsuki.gg",
        secure=True,
        httponly=True,
        samesite="strict",
    )
    return http_response
