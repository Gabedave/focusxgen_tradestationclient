from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

router = APIRouter()

templates = Jinja2Templates(directory="assets/templates")

@router.get("/home", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", 
    {"request":request, 
    "order_ids": [121324,12312,232342,5324],
    "balances":[
        {'AccountID':'12345678','CashBalance':'900'},
        {'AccountID':'12345678','CashBalance':'900'},
        {'AccountID':'12345678','CashBalance':'900'},
        {'AccountID':'12345678','CashBalance':'900'},
        {'AccountID':'12345678','CashBalance':'900'},
        {'AccountID':'12345678','CashBalance':'900'}
        ]})