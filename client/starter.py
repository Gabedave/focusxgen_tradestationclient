"""Module for IQ Option API starter."""

import os
import logging
import sys
import time
from pprint import pprint

from ts.client import TradeStationClient

import config.settings as constants



class Client(object):
    """Calls for TradeStationClient API."""

    def __init__(self, config):
        """
        :param config: The instance of :class:`Settings
            <iqoptionpy.settings.settigns.Settings>`.
        """
        self.config = config
        self.api = TradeStationClient(
            username=self.config['username'],
            client_id=self.config['client_id'],
            client_secret=self.config['client_secret'],
            redirect_uri=self.config['redirect_uri'],
            scope=self.config['scope'],
            paper_trading=self.config['paper_trading']
        )

    def create_connection(self):
        """Method for create connection to IQ Option API."""
        logger = logging.getLogger(__name__)
        logger.info("Create connection.")

        try:
            check, reason = self.api.connect()
        except Exception as e:
            logger.info('Error: ', e)
            return None

        if check:
            logger.info("Successfully connected.")
            if self.api.check_connect == False:
                logger.info("Websocket did not respond")
                return None
        else:
            logger.info("Connection Failed")
            logger.error(reason)
            raise
            # return None
        return check, reason

    def start_signalers(self, stockframe):
        """Method for start signalers."""
        logger = logging.getLogger(__name__)
        logger.info("Create signalers.")
        signalers = []
        patterns = self.config.get_trade_patterns()
        
        for active in self.actives:
            signaler = create_signaler(self.api, active, stockframe, self.balance)
            signaler.set_patterns(patterns)
            signaler.start()
            signalers.append(signaler)
        return signalers

    def start_traders(self):
        """Method for start traders."""
        logger = logging.getLogger(__name__)
        logger.info("Create traders.")
        traders = []
    
        for active in self.actives:
            trader = create_trader(self.api, active)
            trader.start()
            traders.append(trader)
        return traders
    
    def update_balance(self):
        self.balance = self.api.get_balance()

    def change_balance_mode(self, balance_mode):
        """Method to select balance mode."""
        self.api.change_balance(balance_mode)
        self.balance = self.api.get_balance()
        
        logger = logging.getLogger(__name__)
        logger.info("Changed balance to {}. Balance is {}".format(balance_mode,self.balance))
        return balance_mode, self.balance

    def start_data_frame(self):
        """Set up data frame"""
        logger = logging.getLogger(__name__)

        price_df = Robot(self.api, self.actives)
        price_df.initiate_frame()
        price_df.add_indicators()
        logger.info("Stockframe initiated and indicators added")
        return price_df
    
    def check_open_markets(self):
        logger = logging.getLogger(__name__)

        all_markets = self.api.get_all_open_time()
        current_open_markets = []
        actives_not_open = []

        for dirr in (['binary','turbo']):
            for symbol in all_markets[dirr]: 
                if all_markets[dirr][symbol]['open'] == True:
                    current_open_markets.append(symbol)

        for active in self.config.get_trade_actives():
            if active not in current_open_markets:
                actives_not_open.append(active)
        
        current_open_markets = list(set(self.config.get_trade_actives()) - set(actives_not_open))

        if actives_not_open:
            logger.info("{} not open right now".format(actives_not_open))
            logger.info("{} open".format(current_open_markets))
        else:
            logger.info(f"All symbols open {self.actives}")
        
        self.actives = current_open_markets
        if current_open_markets == []:
            logger.info('Market closed for all actives')
            return None
        time.sleep(2)
        return self.actives


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


if __name__ == '__main__':
    config = {**constants.CONNECTION_SETTINGS}
    config['username'] = 'Test'
    config['client_id'] = 'adsfa'
    config['client_secret'] = 'adsf'
    pprint(config)
    client = Client(config)
    pprint(client.api)

