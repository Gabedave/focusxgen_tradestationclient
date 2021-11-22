from fastapi import APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

router = APIRouter()

templates = Jinja2Templates(directory="assets/templates")

@router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse('login.html', {'request':request})

@router.get("/login")
async def login():
    return RedirectResponse(url='/')