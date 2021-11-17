from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

router = APIRouter()

templates = Jinja2Templates(directory="assets/templates")

@router.get("/home", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request":request})