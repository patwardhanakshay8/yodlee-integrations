# Live Prices for Mutual Funds and Stocks

import unirest,requests
from django.conf import settings


def mutual_fund_live_price(scheme_code):
	
	mutual_fund_price = ""
	
	params = ("{\"scodes\":[" + str(scheme_code)  + "]}")

	# mashape api for fetching mutual fund prices
	# https://market.mashape.com/nviror/mutual-funds-nav-india
	response = unirest.post("https://mutualfundsnav.p.mashape.com/",
		headers={
				"X-Mashape-Key": settings.MASHAPE_API_KEY,
				"Content-Type": "application/json",
				"Accept": "application/json"
				},
			params=params
		)
	
	# sample response for the mashape api response.body = [{u'date': u'2017-01-16', u'nav': u'10.9033', u'scode': 138220}]		
	
	if type(response.body) is list:
		mutual_fund_price = response.body[0]['nav']
	else:
		mutual_fund_price = 'N/A'

	return mutual_fund_price

def stock_live_price(ticker):

	stock_live_price = ""

	# quandl api for live prices for stocks
	response = requests.get('https://www.quandl.com/api/v3/datasets/' + ticker + '.json?api_key=' + settings.QUANDL_API_KEY )			
	response = response.json()
	
	if 'dataset' in response:
		stock_live_price = response['dataset']['data'][0][5]
	else:
		stock_live_price = 'N/A'

	return stock_live_price

def convert_currency(from_currency,to_currency):

	# apilayer api
	exchange_response = requests.get('https://apilayer.net/api/convert?access_key=' + settings.API_LAYER_KEY + '&from=' + from_currency + '&to=' + to_currency + '&amount=1&format=1').json()

	return exchange_response['result']

