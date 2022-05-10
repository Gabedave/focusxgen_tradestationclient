from email import message
from pprint import pprint
from fastapi import APIRouter, Response, Request, background, status, Form, BackgroundTasks
from typing import Optional, Union
from datetime import datetime
from http import HTTPStatus

import asyncio
import concurrent
import multiprocessing
import json
import os
import sys
import time

from config import settings
from client.starter import Client


class Positions():
    def __init__(self):
        self.stream = False
        self.pool = False

    def start(self):
        self.stream = True
        print("Starting Executor")
        get_all_positions_mod(self.pool)

    def shutdown(self):
        self.pool.close()
        print("Executor Closed")
        self.stream = False


class Base():
    positions = None

    def reset(self):
        if self.positions:
            self.positions.shutdown()
        self.config = settings.load_config()
        self.client = Client(self.config)
        self.positions = Positions()


base = Base()
base.reset()

router = APIRouter()

@router.get("/api/accounts")
async def accounts():
    all_profiles = []
    for profile in base.client.client.values():
        all_profiles.append({
            "username" : profile.config["username"],
            "client_id" : profile.config["client_id"],
            "log_in" : profile.state['logged_in'],
            "auth_state" : profile.authstate
        })
    return all_profiles

@router.get("/api/start")
async def start():
    allow_login = False
    for client_id, profile in base.client.client.items():
        if profile.state['logged_in'] and profile.authstate:
            base.client.save_login(client_id)
            allow_login = True

    if allow_login: return {
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
async def posit(background_tasks: BackgroundTasks):
    try:
        if not base.positions.stream:
            print("starting stream")
            await stream(background_tasks)
        
        else:
            return {
                "success": True,
                "data": base.client.positions
            }
    except Exception as e:
        return {
            "success": False,
            "errors": {
                "error": "Internal error",
                "detail": e.message
            }
        }
    
# Positions Process
def get_all_positions_mod(executor):
    while True:
        print("...getting positions")
        
        start_ = time.time()

        def run(positions):
            loop = asyncio.new_event_loop()
            try:
                loop.run_until_complete(base.client.get_all_positions())
                # asyncio.run()
            except Exception as e:
                positions.stream = False
                print("Error in Background task", e)
                positions.shutdown()
                # sys.exit()
            finally:
                loop.close()
        
        executor.apply_async(run(base.positions))
        
        posit = base.client.positions
        # print(posit)
        end = time.time() - start_
        if end < 1.2:
            time.sleep(1.2 - end)

def positions_task():
    # loop = asyncio.get_event_loop()
    # asyncio.set_event_loop(loop)
    with multiprocessing.Pool(os.cpu_count()) as p:
        # loop = asyncio.new_event_loop()
        base.positions.pool = p
        
        base.positions.start()
    

@router.get("/api/positions/stream", status_code=HTTPStatus.ACCEPTED)
async def stream(background_task: BackgroundTasks):
    if base.positions.stream:
        print("..stream already running")
    else:
        background_task.add_task(positions_task)
    
    return {
        "success": True
    }
# Positions Process

@router.get("/api/trader/{mode}")
async def trader_mode(response: Response, mode: str):
    if mode == "paper":
        if await base.client.change_trading_mode(True):
            return await start()
        else: return {
            "success": False,
            "errors": {
                "error": "Change Trading Mode failed"
            }
        }
    elif mode == "real":
        if await base.client.change_trading_mode(False):
            return await start()
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
        strike_price_dict = await base.client.get_symbol_info(symbol, option)
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
        order_store = await base.client.sort_orders()
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
    Symbol: Optional[str] = Form(None),
    ExpirationDate: Optional[str] = Form(None),
    StrikePrice: Optional[float] = Form(None),
    TradeAction: str = Form(...),
    OptionName: str = Form(...),
    Quantity: int = Form(...),
    LimitPrice: Optional[str] = Form(None),
    StopPrice: Optional[str] = Form(None),
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
    Mode: Optional[str] = Form(None),
    OrderId: Optional[str] = Form(None),
    TrailingStop: Optional[str] = Form(None),
    TrailingValue: Optional[float] = Form(None)
    ):
    try:
        if Symbol: Symbol = Symbol.strip()
        TimeInForce = {"Duration": "DAY"}
        if ExpirationDate:
            TimeInForce["Expiration"] = datetime.strptime(ExpirationDate.split(' - ')[0], '%Y-%m-%d %H:%M:%S').isoformat('T') + 'Z'
        
        if OpenOrClose == "Open":
            TradeAction_ = "BUYTOOPEN"
        elif OpenOrClose == "Close":
            TradeAction_ = "SELLTOCLOSE"
        else: raise ValueError("Invalid OpenOrClose")

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
            assembled[x]["Symbol"] = Symbol if Symbol else OptionName.split(" ")[0]
            assembled[x]["TriggerKey"] = "STT"
        ActivationRules = [y for x,y in assembled.items()]
        # print(ActivationRules)

        order = {
            "OrderType": OrderType,
            "TimeInForce": TimeInForce,
            "Quantity": str(Quantity),
            "Symbol": OptionName,
            "StrikePrice": str(StrikePrice),
            "TradeAction": TradeAction_,
            "Route": "Intelligent"
        }

        if OrderType == 'Limit' or OrderType == 'StopLimit':
            order['LimitPrice'] = str(LimitPrice)

        if OrderType == 'StopLimit' or OrderType == 'StopMarket':
            order['StopPrice'] = str(StopPrice)

        if ActivationRules != []:
            order['AdvancedOptions'] = {"MarketActivationRules" : ActivationRules}

        if TrailingStop:
            if TrailingStop == "Amount":
                order['AdvancedOptions'] = {
                    "TrailingStop" : {
                        "Amount": str(TrailingValue)
                    }
                }
            elif TrailingStop == "Percent":
                order['AdvancedOptions'] = {
                    "TrailingStop" : {
                        "Amount": str(TrailingValue)
                    }
                }

        pprint(order)
        
        if kind == 'confirm':
            resp = await base.client.confirm_order(order)
        elif kind == 'execute':
            if Mode == "ModifyOrder":
                OrderId = OrderId.strip()
                print("modify")
                resp = await base.client.modify_order(OrderId, {x: y for x, y in order.items() \
                    if x in ["Symbol", "Quantity", "OrderType", "LimitPrice", "StopPrice", "AdvancedOptions"]})
                await base.client.store_store()
            else:
                resp = await base.client.execute_order(order)
                await base.client.store_orders(resp)
        else: raise Exception("Wrong Order Type")
        
        return resp

    except Exception as e:
        #print(e)
        raise Exception(e)
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            'errors': {
                'error': f'Failed to {kind} order',
                'details': str(e)
            }
        }
    

@router.get("/api/cancelorder/{orderId}")
async def cancel_order(orderId: str):
    try:
        success = True
        cancelled = await base.client.cancel_order(orderId)

        for client_id in cancelled:
            if "Error" in cancelled[client_id]:
                success = False
        if success == False: raise Exception(cancelled[client_id]['Message'])
        await base.client.store_store()
        return {
            "success": True,
            "data": {
                "items": cancelled,
                "msg": "Orders successfully canceled."
            }
        }
    except Exception as e:
        raise Exception(e)
        # print(e)
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
    return base.client

def pool_():
    return base.positions
    