from typing import Optional
from datetime import datetime
import asyncio
from fastapi import APIRouter, Form, status
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from .api import client

router = APIRouter()

templates = Jinja2Templates(directory="assets/templates")

@router.get("/home", response_class=HTMLResponse)
async def home(request: Request):
    trading_mode = "SIM" if client.paper_trading else "LIVE"
    return templates.TemplateResponse("home.html",
    {
        "request": request,
        "clients": client,
        "tradingMode": trading_mode.upper()
    })

# @router.post("/home")
# async def create_order(
#     request: Request,
#     response: Response,
#     Quantity: int = Form(...), 
#     Symbol: str = Form(...), 
#     OrderType: str = Form(...),
#     LimitPrice: Optional[int] = Form(...),
#     ExpirationDate: Optional[str] = Form(...),
#     ActivationRules: Optional[list] = Form(...)):
#     try:
#         TimeInForce = {"Duration": "DAY"}
#         if ExpirationDate:
#             TimeInForce["Expiration"] = datetime.strptime(ExpirationDate.split(' - ')[0], '%Y-%m-%d %H:%M:%S').isoformat('T') + 'Z'
        
#         TradeAction = "BUY" #BUYTOOPEN  BUYTOCLOSE  SELLTOOPEN  SELLTOCLOSE

#         order = {
#             # "Legs" : [{
#             #     "Quantity": str(Quantity),
#             #     "Symbol": Symbol.strip(),
#             #     "TradeAction": TradeAction
#             # }],
#             "OrderType": OrderType,
#             "TimeInForce": TimeInForce,
#             "Quantity": str(Quantity),
#             "Symbol": Symbol.strip(),
#             "TradeAction": TradeAction,
#             "Route": "Intelligent"
#         }

#         if OrderType == 'Limit':
#             order['LimitPrice'] = str(LimitPrice)

#         if ActivationRules and type(ActivationRules) == [dict]:
#             order['AdvancedOptions'] = {"MarketActivationRules" : ActivationRules}
        
#         # print(order)
#         response = await client.execute_order(order)
#         await client.store_orders(response)

#         return response
    
#     except Exception as e:
#         print(e)
#         response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
#         return {
#             'errors': {
#                 'error': 'Failed to create order',
#             }
#         }
