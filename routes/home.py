from typing import Optional
from datetime import datetime
import asyncio
from fastapi import APIRouter, Form, status
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from .api import client_

router = APIRouter()

templates = Jinja2Templates(directory="assets/templates")

@router.get("/home", response_class=HTMLResponse)
async def home(request: Request):
    trading_mode = "SIM" if client_().paper_trading else "LIVE"
    return templates.TemplateResponse("home.html",
    {
        "request": request,
        "clients": client_(),
        "tradingMode": trading_mode.upper()
    })
