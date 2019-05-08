# CRUD Operations for Models Portfolio

from portfolio.models import *
from utilities.live_prices import *

def add_stock_pool(stock_name,ticker):

	if not StockPool.objects.filter(ticker=ticker):
		stock_pool = StockPool()
		stock_pool.stock_name = stock_name
		stock_pool.ticker = ticker
		stock_pool.live_price = stock_live_price(ticker)		# Find stock_live_price() in utilities/live_price.py
		stock_pool.save()
		return True
	else:
		return False

def update_stock_pool():

	stock_pools = StockPool.objects.all()

	for s in stock_pools:
		if not Stocks.objects.filter(symbol=s.ticker):
			s.delete()
		else:
			s.live_price = stock_live_price(s.ticker)		# Find stock_live_price() in utilities/live_price.py
			s.save()

	return True


def add_mf_pool(scheme_name,scheme_code):

	if not MFPool.objects.filter(scheme_code=scheme_code):
		mf_pool = MFPool()
		mf_pool.scheme_name = scheme_name
		mf_pool.scheme_code = scheme_code
		mf_pool.live_price = mutual_fund_live_price(scheme_code)		# Find mutual_fund_live_price() in utilities/live_price.py
		mf_pool.save()
		return True
	else:
		return False

def update_mf_pool():

	mf_pools = MFPool.objects.all()

	for m in mf_pools:
		if not MutualFund.objects.filter(scheme_code=m.scheme_code):
			m.delete()
		else:
			m.live_price = mutual_fund_live_price(m.scheme_code)		# Find mutual_fund_live_price() in utilities/live_price.py
			m.save()
	return True

def initialize_asset_obj():

	asset_obj = {}

	asset_obj['total'] = 0
	# asset_obj['total_inr'] = 0
	# asset_obj['total_usd'] = 0
	# asset_obj['total_sgd'] = 0
	# asset_obj['total_gbp'] = 0
	asset_obj['details'] = []

	return asset_obj

def asset_in_various_currencies(item,attribute):

	obj = {}

	if item.currency == 'USD':
		obj['amount_inr'] = attribute * USD_TO_INR
		obj['amount_usd'] = attribute
		obj['amount_sgd'] = obj['amount_inr'] / SGD_TO_INR
		obj['amount_gbp'] = obj['amount_inr'] / GBP_TO_INR
	elif item.currency == 'SGD':
		obj['amount_inr'] = attribute * SGD_TO_INR
		obj['amount_usd'] = obj['amount_inr'] / USD_TO_INR
		obj['amount_sgd'] = attribute
		obj['amount_gbp'] = obj['amount_inr'] / GBP_TO_INR
	elif item.currency == 'GBP':
		obj['amount_inr'] = attribute * GBP_TO_INR
		obj['amount_usd'] = obj['amount_inr'] / USD_TO_INR
		obj['amount_sgd'] = obj['amount_inr'] / SGD_TO_INR
		obj['amount_gbp'] = attribute
	else:
		obj['amount_inr'] = attribute
		obj['amount_usd'] = obj['amount_inr'] / USD_TO_INR
		obj['amount_sgd'] = obj['amount_inr'] / SGD_TO_INR
		obj['amount_gbp'] = obj['amount_inr'] / GBP_TO_INR

	return obj

def total_in_various_currencies(asset_list):

	asset_obj = {}

	asset_obj['total_inr'] = sum(item['amount_inr'] for item in asset_list)
	asset_obj['total_usd'] = sum(item['amount_usd'] for item in asset_list)
	asset_obj['total_sgd'] = sum(item['amount_sgd'] for item in asset_list)
	asset_obj['total_gbp'] = sum(item['amount_gbp'] for item in asset_list)

	return asset_obj

def asset_in_inr(currency,value):

	obj = {}

	if currency == 'USD':
		obj['amount_inr'] = value * CurrencyExchange.objects.get(from_currency='USD',to_currency='INR').rate
	elif currency == 'SGD':
		obj['amount_inr'] = value * CurrencyExchange.objects.get(from_currency='SGD',to_currency='INR').rate
	elif currency == 'GBP':
		obj['amount_inr'] = value * CurrencyExchange.objects.get(from_currency='GBP',to_currency='INR').rate
	else:
		obj['amount_inr'] = value

	return obj


# Other Investment

def get_other_investments(client,type_of_investment=None):

	other_investments_obj = initialize_asset_obj()

	def process_other_investment(item):

		other_investment_obj = {}
		other_investment_obj['client'] = item.client.client.username
		other_investment_obj['type_of_investment'] = item.type_of_investment
		other_investment_obj['description'] = item.description
		other_investment_obj['source'] = item.source
		other_investment_obj['holding_id'] = item.holding_id
		other_investment_obj['currency'] = item.currency
		other_investment_obj['value'] = item.value

		other_investment_obj.update(asset_in_inr(item.currency,item.value))

		return other_investment_obj

	if type_of_investment:
		other_investments = OtherInvestment.objects.filter(client=client,type_of_investment=type_of_investment)
	else:
		other_investments = OtherInvestment.objects.filter(client=client)

	if other_investments:
		other_investments_list = []

		for item in other_investments:
			other_investments_list.append(process_other_investment(item))

		other_investments_obj['total'] = sum(item['amount_inr'] for item in other_investments_list)
		other_investments_obj['details'] = other_investments_list

	return other_investments_obj

def add_or_update_other_investment(client,values):

	if OtherInvestment.objects.filter(client=client,type_of_investment=values['type_of_investment'],description=values['description'],holding_id=values['holding_id']):
		other_investment = OtherInvestment.objects.get(client=client,type_of_investment=values['type_of_investment'],description=values['description'],holding_id=values['holding_id'])
		other_investment.value = values['value']
		other_investment.save()
		return 'Updated'

	else:
		other_investment = OtherInvestment()
		other_investment.client = client
		other_investment.type_of_investment = values['type_of_investment']
		other_investment.description = values['description']
		other_investment.source = values['source']
		other_investment.holding_id = values['holding_id']
		other_investment.currency = values['currency']
		other_investment.value = values['value']
		other_investment.save()
		return 'Added'

def remove_other_investment(client,values):

	if OtherInvestment.objects.filter(client=client,type_of_investment=values['type_of_investment'],description=values['description'],holding_id=values['holding_id']):
		other_investment = OtherInvestment.objects.get(client=client,type_of_investment=values['type_of_investment'],description=values['description'],holding_id=values['holding_id'])
		other_investment.delete()
		return True

	else:
		return False

# Mutual Funds

def get_mutual_funds(client,type_of_mf=None):

	mutual_funds_obj = initialize_asset_obj()

	def process_mutual_fund(item):

		mf_obj = {}
		mf_obj['client'] = item.client.client.username
		mf_obj['title'] = item.title
		mf_obj['source'] = item.source
		mf_obj['holding_id'] = item.holding_id
		mf_obj['scheme_code'] = item.scheme_code
		mf_obj['mf_type'] = item.mf_type
		mf_obj['quantity'] = item.quantity
		mf_obj['currency'] = item.currency
		mf_obj['price'] = item.price
		if item.scheme_code == 'scheme_code':
			mf_obj['value'] = item.value
			mf_obj['live_price'] = 'N/A'
		else:
			mf_pool_obj = MFPool.objects.get(scheme_code=item.scheme_code)
			if mf_pool_obj.live_price == 0.0:
				mf_obj['value'] = item.value
				mf_obj['live_price'] = 'N/A'
			else:
				mf_obj['value'] = item.quantity * mf_pool_obj.live_price
				mf_obj['live_price'] = mf_pool_obj.live_price
		mf_obj.update(asset_in_inr(item.currency,mf_obj['value']))

		return mf_obj

	if type_of_mf:
		mutual_funds = MutualFund.objects.filter(client=client,mf_type=type_of_mf)
	else:
		mutual_funds = MutualFund.objects.filter(client=client)

	if mutual_funds:

		mutual_funds_list = []

		for item in mutual_funds:
			mutual_funds_list.append(process_mutual_fund(item))

		mutual_funds_obj['total'] = sum(item['amount_inr'] for item in mutual_funds_list)
		mutual_funds_obj['details'] = mutual_funds_list

	return mutual_funds_obj

def add_or_update_mutual_fund(client,values):

	def add_mutual_fund(scheme_code=None):
		mutual_fund = MutualFund()
		mutual_fund.client = client
		mutual_fund.title = values['title']
		if scheme_code:
			mutual_fund.scheme_code = scheme_code
		mutual_fund.quantity = values['quantity']
		mutual_fund.currency = values['currency']
		if 'price' in values:
			mutual_fund.price = values['price']
		else:
			mutual_fund.price = 0
		mutual_fund.value = values['value']
		mutual_fund.source = values['source']
		mutual_fund.holding_id = values['holding_id']
		mutual_fund.save()

		return 'Added'

	def update_mutual_fund():
		mutual_fund = MutualFund.objects.get(client=client,title=values['title'],holding_id=values['holding_id'])
		mutual_fund.quantity = values['quantity']
		if 'price' in values:
			mutual_fund.price = values['price']
		else:
			mutual_fund.price = 0
		mutual_fund.value = values['value']
		mutual_fund.save()

		return 'Updated'

	if MutualFund.objects.filter(client=client,title=values['title'],holding_id=values['holding_id']):
		return update_mutual_fund()
	else:
		mutual_fund_masters = MFMaster.objects.filter(scheme_name__icontains=values['title'])
		if mutual_fund_masters:
			for m in mutual_fund_masters:
				add_mf_pool(m.scheme_name,m.scheme_code)
				return add_mutual_fund(scheme_code=m.scheme_code)
		else:
			return add_mutual_fund()

def remove_mutual_fund(client,values):

	if MutualFund.objects.filter(client=client,title=values['title'],holding_id=values['holding_id']):
		mutual_fund = MutualFund.objects.get(client=client,title=values['title'],holding_id=values['holding_id'])
		mutual_fund.delete()
		return True
	else:
		return False

# Bonds

def get_bonds(client):

	bonds_obj = initialize_asset_obj()

	def process_bond(item):
		bond_obj = {}
		bond_obj['client'] = item.client.client.username
		bond_obj['title'] = item.title
		bond_obj['source'] = item.source
		bond_obj['symbol'] = item.symbol
		bond_obj['series'] = item.series
		bond_obj['holding_id'] = item.holding_id
		bond_obj['quantity'] = item.quantity
		bond_obj['currency'] = item.currency
		bond_obj['price'] = item.price

		if item.symbol == 'bond_symbol':
			bond_obj['value'] = item.value
			bond_obj['live_price'] = 'N/A'
		else:
			bond_master_obj = BondMaster.objects.get(symbol=item.symbol)
			bond_master_obj = BondMaster.objects.get(symbol=item.symbol,series=item.series)
			bond_obj['value'] = item.quantity * bond_master_obj.face_value
			bond_obj['live_price'] = bond_master_obj.face_value
		bond_obj.update(asset_in_inr(item.currency,bond_obj['value']))

		return bond_obj

	bonds = Bond.objects.filter(client=client)

	if bonds:
		bonds_list = []

		for item in bonds:
			bonds_list.append(process_bond(item))

		bonds_obj['total'] = "%.2f" % (sum(item['amount_inr'] for item in bonds_list))
		bonds_obj['details'] = bonds_list

	return bonds_obj

def add_or_update_bond(client,values):

	if Bond.objects.filter(client=client,title=values['title'],holding_id=values['holding_id']):
		bond = Bond.objects.get(client=client,title=values['title'],holding_id=values['holding_id'])
		bond.quantity = values['quantity']
		bond.price = values['price']
		bond.value = values['value']
		bond.save()
		return 'Updated'
	else:
		bond = Bond()
		bond.client = client
		bond.title = values['title']
		bond.holding_id = values['holding_id']
		bond.quantity = values['quantity']
		bond.currency = values['currency']
		bond.price = values['price']
		bond.value = values['value']
		bond.source = values['source']
		bond.save()
		return 'Added'

def remove_bond(client,values):

	if Bond.objects.filter(client=client,title=values['title'],holding_id=values['holding_id']):
		bond = Bond.objects.get(client=client,title=values['title'],holding_id=values['holding_id'])
		bond.delete()
		return True
	else:
		return False

# Stocks

def get_stocks(client):

	stocks_obj = initialize_asset_obj()

	def process_stock(item):
		stock_obj = {}
		stock_obj['client'] = item.client.client.username
		stock_obj['title'] = item.title
		stock_obj['source'] = item.source
		stock_obj['symbol'] = item.symbol
		stock_obj['holding_id'] = item.holding_id
		stock_obj['quantity'] = item.quantity
		stock_obj['currency'] = item.currency
		stock_obj['price'] = item.price

		if item.symbol == 'stock_symbol':
			stock_obj['value'] = item.value
			stock_obj['live_price'] = 'N/A'
		else:
			stock_pool_obj = StockPool.objects.get(ticker=item.symbol)
			stock_obj['value'] = item.quantity * stock_pool_obj.live_price
			stock_obj['live_price'] = stock_pool_obj.live_price
		stock_obj.update(asset_in_inr(item.currency,stock_obj['value']))

		return stock_obj

	stocks = Stocks.objects.filter(client=client)

	if stocks:
		stocks_list = []

		for item in stocks:
			stocks_list.append(process_stock(item))

		stocks_obj['total'] = "%.2f" % (sum(item['amount_inr'] for item in stocks_list))
		stocks_obj['details'] = stocks_list

	return stocks_obj

def add_or_update_stock(client,values):

	def add_stock(ticker=None):
		stock = Stocks()
		stock.client = client
		stock.title = values['title']
		if ticker:
			stock.symbol = s.ticker
		stock.quantity = values['quantity']
		stock.currency = values['currency']
		stock.price = values['price']
		stock.value = values['value']
		stock.source = values['source']
		stock.holding_id = values['holding_id']
		stock.save()
		return 'Added'

	def update_stock():
		stock = Stocks.objects.get(client=client,title=values['title'],holding_id=values['holding_id'])
		stock.quantity = values['quantity']
		stock.price = values['price']
		stock.value = values['value']
		stock.save()
		return 'Updated'

	if Stocks.objects.filter(client=client,title=values['title'],holding_id=values['holding_id']):
		return update_stock()
	else:
		stock_title = values['title'].split()
		if len(stock_title) > 2:
			stock_title = stock_title[0] + ' ' + stock_title[1]
		else:
			stock_title = stock_title[0]
		stock_masters = StockMaster.objects.filter(stock_name__icontains=stock_title)
		if stock_masters:
			for s in stock_masters:
				add_stock_pool(s.stock_name,s.ticker)
				return add_stock(s.ticker)
		else:
			return add_stock()

def remove_stock(client,values):

	if Stocks.objects.filter(client=client,title=values['title'],holding_id=values['holding_id']):
		stock = Stocks.objects.get(client=client,title=values['title'],holding_id=values['holding_id'])
		stock.delete()
		return True
	else:
		return False


# Transfer mutual funds in other investments to mutual funds table
def other_investments_to_mutual_funds():

	def process_other_investments(other_investments,type_of_mf):

		for other_investment in other_investments:
			mutual_fund = MutualFund()
			mutual_fund.title = other_investment.description
			mutual_fund.source = other_investment.source
			mutual_fund.holding_id = other_investment.holding_id
			mutual_fund.mf_type = type_of_mf
			mutual_fund.quantity = 0.0
			mutual_fund.currency = other_investment.currency
			mutual_fund.price = 0.0
			mutual_fund.value = other_investment.value
			mutual_fund.save()

		return 'Other Investments ' + type_of_mf + ' -> MFs'

	other_investments_mf_equity = OtherInvestment.objects.filter(type_of_investment='Mutual Fund Equity')

	other_investments_mf_debt = OtherInvestment.objects.filter(type_of_investment='Mutual Fund Debt')

	return process_other_investments(other_investments_mf_equity,'Equity') + process_other_investments(other_investments_mf_debt,'Debt')
