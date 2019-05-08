from portfolio.map_assets import *
from portfolio.models import *

def get_equity(client):

	equity_obj = {}

	equity_obj['stocks'] = get_stocks(client)				#Find get_stocks() in portfolio/map_assets.py
	equity_obj['mutual_funds_equity'] = get_mutual_funds(client,'Equity')			#Find get_mutual_funds() in portfolio/map_assets.py

	equity_obj['total'] = float(equity_obj['stocks']['total']) + float(equity_obj['mutual_funds_equity']['total'])

	return equity_obj

def get_fixed_income(client):

	fixed_income_obj = {}

	fixed_income_obj['others'] = get_other_investments(client,'Other')				#Find get_other_investments() in portfolio/map_assets.py
	fixed_income_obj['savings_accounts'] = get_other_investments(client,'Savings Account')
	fixed_income_obj['deposits'] = get_other_investments(client,'Deposits')
	fixed_income_obj['post_offices'] = get_other_investments(client,'Post Office')
	fixed_income_obj['ulips'] = get_other_investments(client,'ULIP')
	fixed_income_obj['insurances'] = get_other_investments(client,'Insurance')
	fixed_income_obj['epfs'] = get_other_investments(client,'EPF')
	fixed_income_obj['ppfs'] = get_other_investments(client,'PPF')
	fixed_income_obj['mutual_funds_debt'] = get_mutual_funds(client,'Debt')			#Find get_mutual_funds() in portfolio/map_assets.py
	fixed_income_obj['bonds'] = get_bonds(client)		#Find get_bonds() in portfolio/map_assets.py

	fixed_income_obj['total'] = float(fixed_income_obj['others']['total']) + float(fixed_income_obj['savings_accounts']['total']) + float(fixed_income_obj['deposits']['total']) + float(fixed_income_obj['post_offices']['total']) + float(fixed_income_obj['ulips']['total']) + float(fixed_income_obj['insurances']['total']) + float(fixed_income_obj['epfs']['total']) + float(fixed_income_obj['ppfs']['total']) + float(fixed_income_obj['mutual_funds_debt']['total']) + float(fixed_income_obj['bonds']['total'])

	return fixed_income_obj

def get_gold(client):

	gold_obj = {}

	gold_obj['golds'] = get_other_investments(client,'Gold')			#Find get_other_investments() in portfolio/map_assets.py

	return gold_obj

def get_real_estate(client):

	real_estate_obj = {}

	real_estate_obj['real_estates'] = get_other_investments(client,'Real Estate')		#Find get_other_investments() in portfolio/map_assets.py

	return real_estate_obj

def get_total_portfolio(client):

	# Local functions
	return get_equity(client)['total'] + get_fixed_income(client)['total'] + float(get_gold(client)['golds']['total']) + float(get_real_estate(client)['real_estates']['total'])

def get_equity_percentage(client):

	if get_total_portfolio(client) > 0:

		# Local functions
		return ( float(get_equity(client)['total']) / get_total_portfolio(client) ) * 100

	return 0

def get_fixed_income_percentage(client):

	if get_total_portfolio(client) > 0:

		# Local functions
		return ( float(get_fixed_income(client)['total']) / get_total_portfolio(client) ) * 100

	return 0

def get_real_estate_percentage(client):

	if get_total_portfolio(client) > 0:

		#Local functons
		return ( float(get_real_estate(client)['real_estates']['total']) / get_total_portfolio(client) ) * 100

	return 0

def get_gold_percentage(client):

	if get_total_portfolio(client) > 0:

		#Local functions
		return ( float(get_gold(client)['golds']['total']) / get_total_portfolio(client) ) * 100

	return 0

def get_return_fixed(client):

	if get_total_portfolio(client) > 0:

		#Local functions
		return (get_fixed_income(client)['total'] / get_total_portfolio(client))*100

	return 0

def get_return_varied(client):

	if get_total_portfolio(client) > 0:

		#Local functions
		return ( ( get_equity(client)['total'] + float(get_gold(client)['golds']['total']) + float(get_real_estate(client)['real_estates']['total']) ) / get_total_portfolio(client) ) * 100

	return 0

def get_risk_low(client):

	if get_total_portfolio(client) > 0:

		#Local functions
		#Find get_mutual_funds() in portfolio/map_assets.py
		return ( ( get_fixed_income(client)['total'] - float(get_mutual_funds(client,'Debt')['total']) ) / get_total_portfolio(client) ) * 100

	return 0

def get_risk_moderate(client):

	if get_total_portfolio(client) > 0:

		#Local functions
		#Find get_mutual_funds() in portfolio/map_assets.py
		return ( ( get_equity(client)['total'] + float(get_mutual_funds(client,'Debt')['total']) ) / get_total_portfolio(client) ) * 100

	return 0

def get_risk_high(client):

	if get_total_portfolio(client) > 0:

		#Local functions
		return ( float(get_real_estate(client)['real_estates']['total']) / get_total_portfolio(client) ) * 100

	return 0

def get_maturity_short(client):

	if get_fixed_income(client)['total'] > 0:

		#Local function get_fixed_income()
		#Find get_other_investments(), get_mutual_funds() in portfolio/map_assets.py
		return ( ( float(get_other_investments(client,'Savings Account')['total']) + float(get_mutual_funds(client,'Debt')['total']) ) / get_fixed_income(client)['total'] ) * 100

	return 0

def get_maturity_long(client):

	if get_fixed_income(client)['total'] > 0:

		#Local function get_fixed_income()
		#Find get_other_investments(), get_other_investments(), get_mutual_funds() in portfolio/map_assets.py
		return ( ( get_fixed_income(client)['total'] - ( float(get_other_investments(client,'Savings Account')['total']) + float(get_mutual_funds(client,'Debt')['total']) ) ) / get_fixed_income(client)['total'] ) * 100

	return 0

def get_assets_in_currency(client,currency):

	total  = 0.0

	equity_assets = get_equity(client)			# Local function

	for item in ( equity_assets['stocks']['details'] + equity_assets['mutual_funds_equity']['details'] ):

		if item['currency'] == currency:

			total += float(item['amount_inr'])

	fixed_income_assets = get_fixed_income(client)				#Local function

	for item in ( fixed_income_assets['others']['details'] + fixed_income_assets['savings_accounts']['details'] + fixed_income_assets['deposits']['details'] + fixed_income_assets['post_offices']['details'] + fixed_income_assets['ulips']['details'] + fixed_income_assets['insurances']['details'] + fixed_income_assets['mutual_funds_debt']['details'] + fixed_income_assets['bonds']['details'] + fixed_income_assets['epfs']['details'] + fixed_income_assets['ppfs']['details'] ):

		if item['currency'] == currency:

			total += float(item['amount_inr'])

	for item in get_gold(client)['golds']['details']:			#Local function

		if item['currency'] == currency:

			total += float(item['amount_inr'])

	for item in get_real_estate(client)['real_estates']['details']:		#Local function

		if item['currency'] == currency:

			total += float(item['amount_inr'])

	return total

def get_currency_inr(client):

	if get_total_portfolio(client) > 0:

		# Local functions
		return ( get_assets_in_currency(client,'INR') / get_total_portfolio(client) ) * 100

	return 0

def get_currency_usd(client):

	if get_total_portfolio(client) > 0:

		# Local functions
		return ( get_assets_in_currency(client,'USD') / get_total_portfolio(client) ) * 100

	return 0
