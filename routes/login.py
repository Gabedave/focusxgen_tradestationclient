from typing import Optional
from fastapi import APIRouter, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from .api import client_, pool_
client = client_()
positions = pool_()

router = APIRouter()

templates = Jinja2Templates(directory="assets/templates")

active_client_id:str

@router.get("/", response_class=HTMLResponse)
async def root(request: Request, code: Optional[str] = None, state: Optional[str]  = None):
    if positions.stream: 
        positions.shutdown()
        print('...shutting down')
    if code:
        client.profile_complete_login(active_client_id, str(request.url))
    return templates.TemplateResponse('login.html', {'request':request})

@router.get("/login")
async def login(client_id: Optional[str] = None):
    if not client_id:
        return RedirectResponse('/')
    else:
        url = await client.profile_login(client_id)
        if type(url) == str:
            global active_client_id
            active_client_id = client_id
            return RedirectResponse(url)
        elif url == True:
            return RedirectResponse('/')
        else:
            return {
                "success": False,
                "errors": {
                    "error": "Login Error"
                }
            }

@router.get("/logout")
async def logout(response: Response):
    if await client.logout():
        return {
            "success": True, 
            "data": {
                "error", "Logout successful"
            }
        }
    else:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            "success": False, 
            "errors": {
                "error", "Logout unsuccessful"
            }
        }


