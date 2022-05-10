"""Module for TradeStationClient API starter."""

import os
import logging
import sys
import time
import asyncio
import json
from copy import deepcopy
from typing import Union
from pprint import pprint
from datetime import datetime

from ts.client import TradeStationClient

import config.settings as settings


class Client(object):
    """Calls for TradeStationClient API."""

    def __init__(self, config: list):
        """ Initializes the FocusXgen Client
        
         Arguments:
        ----
        config (list): The list of configurations for each profile
        """
        self.config = config
        self.configure_profiles(True)
        self.paper_trading
        self.client__ = []
        self.positions = None

        dir_path = os.getcwd()
        filename = 'store.json'
        file_path = os.path.join(dir_path, 'client/orders', filename)

        if os.path.isfile(file_path):
            with open(file=file_path) as f:
                self.store = json.load(fp=f)
                # pprint(self.store)
        else: self.store = {}

    def configure_profiles(self, paper_trading: bool = True) -> None:
        self.paper_trading = paper_trading
        self.client = {}
        for profile in self.config:
            _profile :TradeStationClient = TradeStationClient(
                username = profile['username'],
                client_id = profile['client_id'],
                client_secret = profile['client_secret'],
                redirect_uri = profile['redirect_uri'],
                scope = profile['scope'],
                paper_trading = paper_trading
            )
            self.client[profile['client_id']] = _profile

    def save_login(self, client_id: str) -> None:
        if client_id not in self.client__:
            self.client__.append(client_id)

    async def profile_login(self, client_id: str) -> Union[str,bool]:
        url = await self.client[client_id].login()
        return url

    async def profile_complete_login(self, client_id: str, full_redirect_uri: str) -> bool:
        # print(client_id, full_redirect_uri)
        res = await self.client[client_id].complete_login(full_redirect_uri)
        return res

    async def logout(self) -> bool:
        try:
            result = await asyncio.gather(*[self.client[x].logout(False) for x in self.client__])
            if result: 
                self.client__.clear()
                return True
            else: raise Exception('Logout Failed')
        except:
            return False

    async def delete(self, client_id) -> bool:
        dir_path = os.getcwd()
        filename = 'config.json'
        file_path = os.path.join(dir_path, 'config', filename)

        if os.path.isfile(file_path):
            with open(file=file_path) as f:
                config = json.load(fp=f)
        config = list(filter(lambda profile: profile['client_id'] != client_id, config))

        with open(file_path, 'w+') as f:
            json.dump(config, f, indent=4)
        
        return True

    async def add(self, data) -> bool:
        dir_path = os.getcwd()
        filename = 'config.json'
        file_path = os.path.join(dir_path, 'config', filename)

        if os.path.isfile(file_path):
            with open(file=file_path) as f:
                config = json.load(fp=f)

        if len(list(filter(lambda x: x['client_id'] == data['client_id'], config))) == 0:
            config.append(data)

            with open(file_path, 'w+') as f:
                json.dump(config, f, indent=4)

                return True
        return False

    def profile_logout(self, client_id: str) -> None:
        try:
            self.client[client_id].logout(temporary=True)
            if client_id in self.client__: self.client__.remove(client_id)
            return True
        except:
            return False

    async def update_balances(self) -> dict:
        new_balances = {}
        for client_id in self.client__:
            profile = self.client[client_id]
            # user_accounts = profile.user_accounts()
            # cash_acccounts = [x['AccountID'] for x in user_accounts if x['AccountType'] == "Cash"]
            Balances: dict = profile.account_balances()['Balances'][0].items() #assumption of one account in each profile
            new_balances[client_id] = {key: Balances[key] for key in ['AccountID','CashBalance']}

    async def change_trading_mode(self, paper_trading: bool = True):
        self.configure_profiles(paper_trading)
        # await asyncio.gather(*[self.profile_login(x) for x in self.client.keys()])
        await asyncio.gather(*[self.profile_login(x) for x in self.client__])

        return True

    async def get_all_positions(self) -> dict:
        async def pos(client_id):
            profile = self.client[client_id]
            res = await asyncio.gather(*[profile.account_positions(), profile.account_balances()])
            Positions: list = res[0]['Positions']
            Balances: list = res[1]['Balances']

            # all_positions[client_id] = []
            results = []

            # Append Account Balance to the Position dict
            for p_ in Positions:
                for b_ in Balances:
                    if b_['AccountID'] == p_['AccountID']:
                        p_['CashBalance'] = b_['CashBalance']
                        p_['BuyingPower'] = b_['BuyingPower']
                        p_['Equity'] = b_['Equity']
                        results.append(p_)
            
            if results == []:
                # print(profile.config["AccountID"], profile.config['client_id'])
                new = {"AccountID": list(filter(lambda x: x[1] == 'Margin' or x[1] == 'Cash', profile.config["AccountID"]))[0][0]}
                for b_ in Balances:
                    if b_['AccountID'] == new['AccountID']:
                        new['CashBalance'] = b_['CashBalance']
                        new['BuyingPower'] = b_['BuyingPower']
                        new['Equity'] = b_['Equity']
                results.append(new)  # all_positions[client_id].append(new)

            return (profile.config['client_id'], results)

        # print("self.client__", self.client__)

        gather = await asyncio.gather(*[pos(x) for x in self.client__])
        all_positions = {x: y for x, y in gather}

        self.positions = all_positions

        # print(all_positions)
        return all_positions

    # async def get_all_positions_stream(self):
    #     while True:
    #         res = await self.get_all_positions()
    #         await asyncio.sleep(5)
    #         yield json.dumps(res)
            
    def date_parse(self, data):
        # datetime = int(list(filter(lambda x: x['ExpirationType'] == "Weekly", data))[0]['ExpirationDate'].strip('/Date()/ '))
        datetim = int(data['ExpirationDate'].strip('/Date() '))
        date_range = data['ExpirationType']
        return datetime.fromtimestamp(datetim/1000).strftime('%Y-%m-%d %H:%M:%S') + ' - ' + date_range

    async def get_symbol_info(self, symbol: str, asset_category = None) -> list:
        if self.client__ == []:
            raise Exception('Please Login')
        profile = self.client[self.client__[0]]
        symbol_info = await profile.search_for_symbol(symbol.strip(), asset_category)
        symbol_expiration_time_dict = {}
        # pprint(symbol_info[0])
        for item in symbol_info:
            expiration_date = self.date_parse(item)
            if expiration_date not in symbol_expiration_time_dict:
                symbol_expiration_time_dict[expiration_date] = {}

            if "Description" not in symbol_expiration_time_dict:
                symbol_expiration_time_dict["Description"] = item['Description']

            if str(item["StrikePrice"]) not in symbol_expiration_time_dict[expiration_date]:
                symbol_expiration_time_dict[expiration_date][str(item["StrikePrice"])] = {}

            if item["OptionType"] not in symbol_expiration_time_dict[expiration_date][str(item["StrikePrice"])]:
                symbol_expiration_time_dict[expiration_date][str(item["StrikePrice"])][item["OptionType"]] = item["Name"]

        # pprint(symbol_expiration_time_dict)
        return symbol_expiration_time_dict

    async def execute_order(self, order: dict) -> dict:
        async def execute(x):
            profile = self.client[x]

            if 'AccountID' not in profile.config:
                accounts = [(x['AccountID'], x['AccountType']) for x in (await profile.user_accounts())['Accounts']]
            else: accounts = profile.config['AccountID']
                
            order_ = deepcopy(order)
            order_['AccountID'] = list(filter(lambda x: x[1] == 'Margin' or x[1] == 'Cash', accounts))[0][0]
            
            # pprint({x: order_})
            res = await profile.submit_order(order_)
            if 'Error' in res:
                raise Exception(res['Error'], res['Message'])
            return profile.config['client_id'], res

        gather = await asyncio.gather(*[execute(x) for x in self.client__])
        responses = {x: y for x, y in gather}
        return responses

    async def confirm_order(self, order: dict) -> dict:
        async def execute(x):
            profile = self.client[x]

            if 'AccountID' not in profile.config:
                accounts = [(x['AccountID'], x['AccountType']) for x in (await profile.user_accounts())['Accounts']]
            else: accounts = profile.config['AccountID']
                
            order_ = deepcopy(order)
            order_['AccountID'] = list(filter(lambda x: x[1] == 'Margin' or x[1] == 'Cash', accounts))[0][0]
            
            # pprint(order_)
            res = await profile.confirm_order(order_)
            if 'Error' in res:
                raise Exception(res['Error'])
            return profile.config['client_id'], res

        gather = await asyncio.gather(*[execute(x) for x in self.client__])
        responses = {x: y for x, y in gather}
        return responses

    async def store_orders(self, dict_: dict) -> dict:

        order_id = 'order ' + str(time.time())
        
        order = dict(filter(lambda x: "Error" not in x[1]["Orders"][0], dict_.items()))
        if order != {}:
            self.store[order_id] = order

        dir_path = os.getcwd()
        filename = 'store.json'
        file_path = os.path.join(dir_path, 'client/orders', filename)

        with open(file_path, 'w+') as f:
            json.dump(self.store, f, indent=4)

        return self.store.get(order_id)

    async def store_store(self):
        dir_path = os.getcwd()
        filename = 'store.json'
        file_path = os.path.join(dir_path, 'client/orders', filename)

        with open(file_path, 'w+') as f:
            json.dump(self.store, f, indent=4)

    async def get_all_orders(self):
        async def get(x):
            profile = self.client[x]

            res = await profile.get_orders()
            # pprint(res)

            if res['Errors'] != []:
                raise Exception(res["Errors"])
            return x, res['Orders'] # list(filter(lambda x: x['Status'] not in ['OUT'], res['Orders']))

        gather = await asyncio.gather(*[get(x) for x in self.client__])
        responses = {x: y for x, y in gather}
        return responses

    async def sort_orders(self):
        orders_ = await self.get_all_orders()
        # pprint(orders_)
        
        # if self.store == {}: return self.store
        # for order_id in self.store:
        #     if not self.store[order_id]: del self.store[order_id]
        sorted = {}

        for order_id in deepcopy(list(self.store.keys())):
            for client_id in self.client__:
                if orders_[client_id] == []: continue

                for detail in orders_[client_id]:
                    # if order_id not in self.store.keys(): continue
                    # print(client_id, self.store[order_id][client_id])
                    if client_id not in self.store[order_id]: continue

                    if self.store[order_id][client_id]['Orders'][0]['OrderID'] == detail['OrderID']:
                        
                        sorted[order_id] = sorted.get(order_id, {})
                        sorted[order_id][client_id] = sorted[order_id].get(client_id, self.store[order_id][client_id])

                        sorted[order_id][client_id]['Orders'][0]['AccountID'] = detail['AccountID']
                        sorted[order_id][client_id]['Orders'][0]['StatusDescription'] = detail['StatusDescription']
                        sorted[order_id][client_id]['Orders'][0]['RejectReason'] = detail['RejectReason'] if detail['StatusDescription'] == "Rejected" else ""
                        sorted[order_id][client_id]['Orders'][0]['OrderType'] = detail['OrderType']
                        sorted[order_id][client_id]['Orders'][0]['Legs'] = detail['Legs']
                        if detail["OrderType"] == "Limit":
                            sorted[order_id][client_id]['Orders'][0]['LimitPrice'] = detail['PriceUsedForBuyingPower']
                        if detail["OrderType"] == "StopMarket":
                            sorted[order_id][client_id]['Orders'][0]['StopPrice'] = detail['StopPrice']
                        if detail["OrderType"] == "StopLimit":
                            sorted[order_id][client_id]['Orders'][0]['LimitPrice'] = detail['LimitPrice']
                            sorted[order_id][client_id]['Orders'][0]['StopPrice'] = detail['StopPrice']

                    # else:
                        
                    #     del self.store[order_id]
                    #     continue
        
        # pprint(sorted)
        return sorted
        
    async def cancel_order(self, order_id):
        success = True
        async def cancel(x):
            profile = self.client[x]
    
            res = await profile.cancel_order(self.store[order_id][x]['Orders'][0]['OrderID'])
            # pprint(res)

            # if res['Message'] == "Order successfully canceled.":
            #     del self.store[order_id]

            if "Error" not in res:
                # print(new_order['OrderType'])
                self.store[order_id][x]['Orders'][0]['StatusDescription'] = "Cancelled"
                self.store[order_id][x]['Orders'][0]['Message'] = res["Message"]
            else:
                success = False
            
            return x, res

        gather = await asyncio.gather(*[cancel(x) for x in self.client__])
        responses = {x: y for x, y in gather}

        # if success:
        #     del self.store[order_id]

        return responses

    async def modify_order(self, order_id: str, new_order: dict):
        async def modify(x):
            profile = self.client[x]
    
            res = await profile.replace_order(self.store[order_id][x]['Orders'][0]['OrderID'], new_order)

            switch_orderType = lambda x: {
                "Market": "Market",
                "Limit": f"{new_order.get('LimitPrice')} Limit",
                "StopMarket": f"{new_order.get('StopPrice')} Market",
                "StopLimit": f"Limit Price: {new_order.get('LimitPrice')}, Stop Price: {new_order.get('StopPrice')}"
            }.get(x, "")

            if "Error" not in res:
                print(new_order['OrderType'])
                self.store[order_id][x]['Orders'][0]['Message'] = "Modified order:" \
                + (self.store[order_id][x]['Orders'][0]['Message'].split(new_order['Symbol'])[0][:-3]).split(":")[-1] \
                + new_order['Quantity'] + ' ' \
                + new_order['Symbol'] + ' @ ' \
                + switch_orderType(new_order['OrderType'])
            return x, res

        gather = await asyncio.gather(*[modify(x) for x in self.client__])
        responses = {x: y for x, y in gather}
        # del self.store[order_id]
        return responses
        

def _prepare_logging():
    """Prepare logging for starter."""
    formatter = logging.Formatter(
        "%(asctime)s:%(levelname)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    logs_folder = "logs"
    if not os.path.exists(logs_folder):
        os.makedirs(logs_folder)

    starter_logger = logging.getLogger(__name__)
    starter_logger.setLevel(logging.INFO)

    starter_file_handler = logging.FileHandler(os.path.join(logs_folder, "starter.log"))
    starter_file_handler.setLevel(logging.DEBUG)
    starter_file_handler.setFormatter(formatter)

    starter_logger.addHandler(console_handler)
    starter_logger.addHandler(starter_file_handler)

    api_logger = logging.getLogger("iqoptionapi")

    api_file_handler = logging.FileHandler(os.path.join(logs_folder, "iqapi.log"))
    api_file_handler.setLevel(logging.DEBUG)
    api_file_handler.setFormatter(formatter)

    api_logger.addHandler(console_handler)
    api_logger.addHandler(api_file_handler)

    signaler_logger = logging.getLogger("signaler")
    signaler_logger.setLevel(logging.INFO)

    signaler_file_handler = logging.FileHandler(os.path.join(logs_folder, "signaler.log"))
    signaler_file_handler.setLevel(logging.DEBUG)
    signaler_file_handler.setFormatter(formatter)

    signaler_logger.addHandler(console_handler)
    signaler_logger.addHandler(signaler_file_handler)

    trader_logger = logging.getLogger("trader")
    trader_logger.setLevel(logging.INFO)

    trader_file_handler = logging.FileHandler(os.path.join(logs_folder, "trader.log"))
    trader_file_handler.setLevel(logging.DEBUG)
    trader_file_handler.setFormatter(formatter)

    trader_logger.addHandler(console_handler)
    trader_logger.addHandler(trader_file_handler)

    websocket_logger = logging.getLogger("websocket")
    websocket_logger.setLevel(logging.INFO)

    websocket_file_handler = logging.FileHandler(os.path.join(logs_folder, "websocket.log"))
    websocket_file_handler.setLevel(logging.DEBUG)
    websocket_file_handler.setFormatter(formatter)

    websocket_logger.addHandler(console_handler)
    websocket_logger.addHandler(websocket_file_handler)

    balance_mode_logger = logging.getLogger("balance_mode")
    balance_mode_logger.setLevel(logging.INFO)

    balance_mode_file_handler = logging.FileHandler(os.path.join(logs_folder, "balance_mode.log"))
    balance_mode_file_handler.setLevel(logging.DEBUG)
    balance_mode_file_handler.setFormatter(formatter)

    balance_mode_logger.addHandler(console_handler)
    balance_mode_logger.addHandler(balance_mode_file_handler)


async def main():
    config = settings.load_config()
    # client = Client(config)
    # pprint(client.client)
    # client_id = list(client.client.keys())[0]
    # await client.profile_login(client_id)
    # client.save_login(client_id)
    # pprint(client.profile_complete_login("SM63OK896BoMlmMWy6cQpSmuJkAYlXg6","127.0.0.1:3000/?code=232425232342"))
    # pprint(client.profile_login(config[0]['client_id']))
    # print(client.change_trading_mode())
    # print(client.update_balances())
    # for key, _ in client.client.items():
    #     pprint(_.config)
    # pprint(await client.get_all_positions())
    # pprint(client.get_symbol_info('AAPL'))
    # pprint(await client.execute_order({'Symbol': 'AAPL', 'Quantity': 67, 'OrderType': 'Market', 'TradeAction': 'BUY', 'TimeInForce': {'Duration': 'DAY'}, 'Route': 'Intelligent', 'AccountID': 'SIM1428415X'}))
    # pprint(await client.sort_orders())
    # pprint(await client.cancel_order("order 1639501743.473545"))

if __name__ == '__main__':
    asyncio.run(main())

