from typing import Optional
from client.starter import Client
from fastapi import APIRouter, Response, status, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from .api import client_, pool_, base

router = APIRouter()

templates = Jinja2Templates(directory="assets/templates")

active_client_id:str

@router.get("/", response_class=HTMLResponse)
async def root(request: Request, code: Optional[str] = None, state: Optional[str]  = None):
    if code:
        await client_().profile_complete_login(active_client_id, str(request.url))
        return templates.TemplateResponse('login.html', {'request':request})
    await client_().change_trading_mode(True)
    if pool_().stream:
        pool_().shutdown()
        print('...shutting down')
    return templates.TemplateResponse('login.html', {'request':request})

@router.get("/login")
async def login(client_id: Optional[str] = None):
    if not client_id:
        return RedirectResponse('/')
    else:
        url = await client_().profile_login(client_id)
        print(url)
        if type(url) == str:
            global active_client_id
            active_client_id = client_id
            return RedirectResponse(url)
        elif url == True:
            client_().save_login(client_id)
            return RedirectResponse('/')
        else:
            return {
                "success": False,
                "errors": {
                    "error": "Login Error"
                }
            }

@router.get("/logout")
async def logout():
    if await client_().logout():
        return {
            "success": True,
            "msg": "Logout successful"
        }
    else:
        return {
            "success": False,
            "errors": {
                "error": "Logout unsuccessful"
            }
        }

@router.post("/addaccount")
async def add(
    Username: str = Form(...),
    Client_ID: str = Form(...),
    Client_Secret: str = Form(...),
):

    data = {
        "username" : Username,
        "client_id" : Client_ID,
        "client_secret": Client_Secret
    }

    if await client_().add(data):
        base.reset()
        return {
            "success": True,
            "msg": "Add Account successful"
        }
    else:
        return {
            "success": False, 
            "errors": {
                "error": "Add Account unsuccessful"
            }
        }


@router.get("/delete")
async def delete(client_id: str):
    if await client_().delete(client_id):
        base.reset()
        return {
            "success": True,
            "msg": "Delete successful"
        }
    else:
        return {
            "success": False, 
            "errors": {
                "error": "Delete unsuccessful"
            }
        }

@router.get("/disconnect")
async def disconnect():
    base.reset()

