from __future__ import absolute_import

import os

from celery.task import task

from utilities.live_prices import *
from utilities.yodlee_services import *

from portfolio.models import *
from portfolio.map_assets import *
from portfolio.yodlee_response_process import *
from portfolio.current_portfolio import *

def add_update_currency_exchange_rate(from_currency,to_currency):

	if CurrencyExchange.objects.filter(from_currency=from_currency,to_currency=to_currency):
		currency_exchange = CurrencyExchange.objects.get(from_currency=from_currency,to_currency=to_currency)
		currency_exchange.rate = convert_currency(from_currency,to_currency)		# Find convert_currency() in utilities/live_price.py
		currency_exchange.save()
		return 'Updated'
	else:
		currency_exchange = CurrencyExchange()
		currency_exchange.from_currency = from_currency
		currency_exchange.to_currency = to_currency
		currency_exchange.rate = convert_currency(from_currency,to_currency)		# Find convert_currency() in utilities/live_price.py
		currency_exchange.save()
		return 'Added'

@task(name="currency_converter")
def convert_currencies():

	conversion_status = []

	currencies = ['USD','SGD','GBP']

	for currency in currencies:
		conversion_status.append({
				'from_currency': currency,
				'to_currency': 'INR',
				'status': add_update_currency_exchange_rate(currency,'INR')			# Local function
				})

	return conversion_status

@task(name="asset_pool_update")
def update_asset_pool():

	if update_stock_pool() and update_mf_pool():		# Find update_stock_pool(), update_mf_pool() in portfolio/map_assets.py
		return True
	else:
		return False

@task(name="yodlee_cobrand_session_token_update")
def update_cobrand_session_token():

	os.environ['cobrand_session_token'] = cobrand_login()		# Find cobrand_login() in utilities/yodlee_services.py

	return os.environ['cobrand_session_token']

@task(name="yodlee_client_login")
def yodlee_user_login(username,password):

	mapping_status = []

	cobrand_session_token = os.environ['cobrand_session_token']

	user_session_token = user_login(cobrand_session_token,username,password)		# Find user_login() in utilities/yodlee_services.py

	account_item_ids = get_account_item_list(cobrand_session_token,user_session_token)		# Find get_account_item_list() in utilities/yodlee_services.py

	client = Client.objects.get(client__username=username)

	for item_id in account_item_ids:

		item = get_individual_item(cobrand_session_token,user_session_token,item_id)		# Find get_individual_item() in utilities/yodlee_services.py

		mapping_status.append(process_yodlee_item(client,item))			# Find process_yodlee_item() in portfolio/yodlee_response_process.py

	return mapping_status

def add_update_current_portfolio(client):

	def process_current_portfolio(current_portfolio,equities,fixed_incomes):

		# Find all functions in portfolio/current_portfolio.py
		current_portfolio.equities = get_equity_percentage(client)
		current_portfolio.fixed_income = get_fixed_income_percentage(client)
		current_portfolio.gold = get_gold_percentage(client)
		current_portfolio.real_estate = get_real_estate_percentage(client)
		current_portfolio.equities_value = equities['total']
		current_portfolio.fixed_income_value = fixed_incomes['total']
		current_portfolio.gold_value = get_gold(client)['golds']['total']
		current_portfolio.real_estate_value = get_real_estate(client)['real_estates']['total']
		current_portfolio.risk_low = get_risk_low(client)
		current_portfolio.risk_moderate = get_risk_moderate(client)
		current_portfolio.risk_high = get_risk_high(client)
		current_portfolio.maturity_short = get_maturity_short(client)
		current_portfolio.maturity_long = get_maturity_long(client)
		current_portfolio.return_fixed = get_return_fixed(client)
		current_portfolio.return_varied = get_return_varied(client)
		current_portfolio.currency_inr = get_currency_inr(client)
		current_portfolio.currency_usd = get_currency_usd(client)
		current_portfolio.total_stocks = equities['stocks']['total']
		current_portfolio.total_mf_equity = equities['mutual_funds_equity']['total']
		current_portfolio.total_mf_debt = fixed_incomes['mutual_funds_debt']['total']
		current_portfolio.total_bonds = fixed_incomes['bonds']['total']
		current_portfolio.total_other_investments = float(fixed_incomes['total']) - ( float(fixed_incomes['mutual_funds_debt']['total']) + float(fixed_incomes['bonds']['total']) )
		current_portfolio.total_portfolio = get_total_portfolio(client)

		current_portfolio.save()

		return 'Added'

	equities = get_equity(client)
	fixed_incomes = get_fixed_income(client)

	if CurrentPortfolio.objects.filter(client=client):
		current_portfolio = CurrentPortfolio.objects.get(client=client)

		return process_current_portfolio(current_portfolio,equities,fixed_incomes)

	else:
		current_portfolio = CurrentPortfolio()
		current_portfolio.client = client
		current_portfolio.save()

		return process_current_portfolio(current_portfolio,equities,fixed_incomes)

@task(name="current_portfolio_update")
def add_update_current_portfolios(client=None):

	update_status = []

	if client:

		update_status.append({
				'client' : client.client.username,
				'update_status' : add_update_current_portfolio(client)			# Local function
			})
	else:

		clients = Client.objects.all()

		for client in clients:

			update_status.append({
					'client' : client.client.username,
					'update_status' : add_update_current_portfolio(client)		# Local function
				})

	return update_status
