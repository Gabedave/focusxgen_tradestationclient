"""Module with constants for configuration."""

from pprint import pprint
import json

required_keys_dict = {
	'username' : '',
	'client_id' : '',
	'client_secret' : '',
	'paper_trading' : True,
	'redirect_uri' : 'http://localhost:3000',
	'scope' : ['openid', 'profile', 'offline_access', 'MarketData', 'ReadAccount', 'Trade', 'Crypto']
}

def add_required_keys(dict) -> dict:
	for key in required_keys_dict.keys():
		if key not in dict.keys():
			dict[key] = required_keys_dict[key]

	return dict

def load_config() -> list:
	with open('config/config.json') as f:
		settings = json.load(f)

	connection_settings = [add_required_keys(x) for x in settings]
	return connection_settings

if __name__ == '__main__':
	pprint(load_config())