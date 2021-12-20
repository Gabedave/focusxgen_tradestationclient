from fastapi import APIRouter, Response, Request, status, Form, BackgroundTasks
from typing import Optional, Union
from datetime import datetime
from http import HTTPStatus

import asyncio
import concurrent
import json
import os
import sys
import time

from config import settings
from client.starter import Client

config = settings.load_config()
client = Client(config)
loop = asyncio.new_event_loop() 

router = APIRouter()


class Positions(object):
    def __init__(self):
        self.stream = False
        self.pool = False

    def shutdown(self):
        global shutdown
        shutdown = True

positions = Positions()

@router.get("/api/accounts")
async def accounts():
    all_profiles = []
    for profile in client.client.values():
        all_profiles.append({
            "username" : profile.config["username"],
            "client_id" : profile.config["client_id"],
            "log_in" : profile.state['logged_in'],
            "auth_state" : profile.authstate
        })
    return all_profiles

@router.get("/api/start")
async def start():
    for client_id, profile in client.client.items():
        if profile.state['logged_in'] and profile.authstate:
            client.save_login(client_id)
            return {
                "success": True,
                "data": {
                    "redirect": "/home"
                }
            }
    return {
        "success": False,
        "errors": {
            "error" : "Not logged in",
            "detail" : "You are not logged in to a TradeStation account"
        }
    }

@router.get("/api/positions")
async def posit():
    file_path = os.path.join(os.getcwd(), 'client/positions/positions.json')
    # print(file_path)
    if os.path.isfile(file_path):
        with open(file=file_path) as f:
            pos = json.load(fp=f)
            return {
                'success': True,
                "data": pos
            }
    else: return{
        "success": False,
        "errors": {
            "error": "Internal error"
        }
    }

# Positions Process
def get_all_positions_mod(executor):
    while True:
        print("...getting positions")
        
        global shutdown
        # print("shutdown", shutdown)
        if shutdown:
            executor.shutdown()
            positions.stream = False
            shutdown = False
            sys.exit()
        else:
            executor.submit(asyncio.run(client.get_all_positions()))
        posit = client.positions
        time.sleep(2)
        
        dir_path = os.getcwd()
        filename = 'positions.json'
        file_path = os.path.join(dir_path, 'client/positions', filename)

        with open(file_path, 'w+') as f:
            json.dump(posit, f, indent=4)

def positions_task():
    # loop = asyncio.get_event_loop()
    # asyncio.set_event_loop(loop)
    with concurrent.futures.ProcessPoolExecutor(max_workers=1) as p:
        global shutdown
        shutdown = False
        positions.pool = p
        loop.run_in_executor(positions.pool, get_all_positions_mod(positions.pool))
    

@router.get("/api/positions/stream", status_code=HTTPStatus.ACCEPTED)
async def func(background_task: BackgroundTasks):
    # return StreamingResponse(client.get_all_positions_stream())
    global shutdown
    if positions.stream:
        print("..stream already running")
    else:
        shutdown = False
        background_task.add_task(positions_task)
        positions.stream = True
    
    return {
        "success": True
    }
# Positions Process

@router.get("/api/trader/{mode}")
async def trader_mode(response: Response, mode: str):
    if mode == "paper":
        if client.change_trading_mode(True):
            return {
                "success": True,
                "data": {
                    "msg": "Trading Mode changed to paper"
                }
            }
        else: return {
            "success": False,
            "errors": {
                "error": "Change Trading Mode failed"
            }
        }
    elif mode == "real":
        if client.change_trading_mode(False):
            return {
                "success": True,
                "data": {
                    "msg": "Trading Mode changed to real"
                }
            }
        else: return {
            "success": False,
            "errors": {
                "error": "Change Trading Mode failed"
            }
        }
    else:
        response.status_code = status.HTTP_404_NOT_FOUND

@router.get("/api/order/checksymbol")
async def trader_mode(symbol: str, option: str):
    try:
        strike_price_dict = await client.get_symbol_info(symbol, option)
        # print(strike_price_dict)
    
        if len(strike_price_dict) != 0:
            return {
                "success": True,
                "data": {
                    "msg": "Symbol Search successful",
                    "items": strike_price_dict
                }
            }
        else: return {
            "success": False,
            "errors": {
                "error": "Failed to get symbol",
                "detail": strike_price_dict
            }
        }
    except Exception as e:
        print(e)
        return {
            "success": False,
            "errors": {
                "error": str(e),
            }
        }


@router.get("/api/order/store")
async def get_orders():
    try:
        order_store = await client.sort_orders()
        return {
            "success": True,
            "data": {
                "msg": "Get orders successful",
                "items": order_store
            }
        }
    except Exception as e: 
        # raise Exception(e)
        print(e)
        return {
        "success": False,
        "errors": {
            "error": "Get orders failed",
            "detail": str(e)
        }
    }

@router.post("/api/order/{kind}")
async def create_order(
    response: Response,
    kind: str,
    OpenOrClose: str = Form(...),
    OrderType: str = Form(...), 
    Symbol: str = Form(...),
    ExpirationDate: str = Form(...),
    StrikePrice: float = Form(...),
    TradeAction: str = Form(...),
    OptionName: str = Form(...),
    Quantity: int = Form(...),
    LimitPrice: Optional[str] = Form(None),
    Predicate: Optional[str] = Form(None),
    Price: Optional[float] = Form(None),
    Operator1: Optional[str] = Form(None),
    Predicate1: Optional[str] = Form(None),
    Price1: Optional[float] = Form(None),
    Operator2: Optional[str] = Form(None),
    Predicate2: Optional[str] = Form(None),
    Price2: Optional[float] = Form(None),
    Operator3: Optional[str] = Form(None),
    Predicate3: Optional[str] = Form(None),
    Price3: Optional[float] = Form(None),
    Operator4: Optional[str] = Form(None),
    Predicate4: Optional[str] = Form(None),
    Price4: Optional[float] = Form(None),
    Operator5: Optional[str] = Form(None),
    Predicate5: Optional[str] = Form(None),
    Price5: Optional[float] = Form(None),
    ):
    try:
        TimeInForce = {"Duration": "DAY"}
        if ExpirationDate:
            TimeInForce["Expiration"] = datetime.strptime(ExpirationDate.split(' - ')[0], '%Y-%m-%d %H:%M:%S').isoformat('T') + 'Z'
        
        if TradeAction == "Call":
            TradeAction_ = "BUYTOOPEN" if OpenOrClose == 'Open' else "SELLTOCLOSE"
        elif TradeAction == "Put":
            TradeAction_ = "SELLTOOPEN" if OpenOrClose == 'Open' else "BUYTOCLOSE"
        else: raise ValueError("Invalid TradeAction")

        rules = [ Predicate2, Predicate3, Predicate4, Predicate5, \
                    Price2, Price3, Price4, Price5, Operator1, Operator2, Operator3, Operator4, Operator5]

        def assemble_activation_rules():
            assembled = {}
            if Predicate and Price:
                assembled['0'] = {"Predicate": Predicate, "Price": str(Price)}
            else: return assembled
            if Predicate1 and Price1 and Operator1:
                assembled['1'] = {"Predicate": Predicate1, "Price": str(Price1), "LogicOperator": Operator1}
            else: return assembled
            if Predicate2 and Price2 and Operator2:
                assembled['2'] = {"Predicate": Predicate2, "Price": str(Price2), "LogicOperator": Operator2}
            else: return assembled
            if Predicate3 and Price3 and Operator3:
                assembled['3'] = {"Predicate": Predicate3, "Price": str(Price3), "LogicOperator": Operator3}
            else: return assembled
            if Predicate4 and Price4 and Operator4:
                assembled['4'] = {"Predicate": Predicate4, "Price": str(Price4), "LogicOperator": Operator4}
            else: return assembled
            if Predicate5 and Price5 and Operator5:
                assembled['5'] = {"Predicate": Predicate5, "Price": str(Price5), "LogicOperator": Operator5}
            return assembled

        assembled = assemble_activation_rules()
        for x in assembled:
            assembled[x]['RuleType'] = "Price"
            assembled[x]["Symbol"] = Symbol.strip()
            assembled[x]["TriggerKey"] = "STT"
        ActivationRules = [y for x,y in assembled.items()]
        # print(ActivationRules)

        order = {
            "OrderType": OrderType,
            "TimeInForce": TimeInForce,
            "Quantity": str(Quantity),
            "Symbol": OptionName,    # Symbol.strip(),
            "StrikePrice": str(StrikePrice),
            "TradeAction": TradeAction_,
            "Route": "Intelligent"
        }

        if OrderType == 'Limit':
            order['LimitPrice'] = str(LimitPrice)

        if ActivationRules != []:
            order['AdvancedOptions'] = {"MarketActivationRules" : ActivationRules}
        
        if kind == 'confirm':
            resp = await client.confirm_order(order)
        elif kind == 'execute':
            resp = await client.execute_order(order)
            await client.store_orders(resp)
        else: raise Exception("Wrong Order Type")
        
        return resp
    
    except Exception as e:
        print(e)
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            'errors': {
                'error': f'Failed to {kind} order',
                'details': str(e)
            }
        }
    



@router.get("/api/cancelorder/{orderId}")
async def cancel_order(orderId):
    try:
        cancelled = await client.cancel_order(orderId)

        for client_id in cancelled:
            if "Error" in cancelled[client_id]:
                raise Exception(cancelled[client_id]['Message'])
        return {
            "success": True,
            "data": {
                "items": cancelled,
                "msg": "Orders successfully canceled."
            }
        }
    except Exception as e:
        print(e)
        return {
            "successs": False,
            "errors":{
                "error": "Orders cancellation failed.",
                "detail": str(e)
            }
        }

# @router.get("/api/vieworder/{orderId}")
# async def view_order(orderId):
#     return {"OrderID": "286234131", "OpenedDateTime": "2021-02-24T15:47:45Z", "OrderType": "Market"}

def client_() -> Client:
    return client

def pool_():
    return positions
    