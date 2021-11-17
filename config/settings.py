"""Module with constants for configuration."""

from decouple import config, Csv

CONNECTION_SETTINGS = {
	'paper_trading' : config('PAPER_TRADING', default=True, cast=bool),
	'redirect_uri' : config('REDIRECT', default=''),
	'scope' : config('SCOPE', default='openid, profile, offline_access, MarketData, ReadAccount, Trade, Crypto', cast=Csv())
}

DEBUG = config('DEBUG', default=False, cast=bool)

if __name__ == '__main__':
	print(CONNECTION_SETTINGS)