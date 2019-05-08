# Process Yodlee Responses to map assets

from portfolio.models import *
from portfolio.map_assets import *
from utilities.yodlee_services import *

def process_yodlee_mutual_fund(client,entry,item):

	response_obj = {}

	response_obj['type_of_asset'] = 'Mutual Fund'
	response_obj['status'] = add_or_update_mutual_fund(client,get_holding(entry,item['itemDisplayName']))
	
	return response_obj

def process_yodlee_stock(client,entry,item):

	response_obj = {}

	if Bond.objects.filter(client=client,title=entry['description'],holding_id=entry['holdingId']):
		response_obj['type_of_asset'] = 'Bond'
		response_obj['status'] = add_or_update_bond(client,get_holding(entry,item['itemDisplayName']))
					
	elif OtherInvestment.objects.filter(client=client,description=entry['description'],holding_id=entry['holdingId']):

		response_obj['type_of_asset'] = 'Mutual Fund without quantity',
		response_obj['status'] = add_or_update_other_investment(client,get_other_investment_holding(entry,item['itemDisplayName'],'Gold'))

	elif MutualFund.objects.filter(client=client,title=entry['description'],holding_id=entry['holdingId']):

		response_obj['type_of_asset'] = 'Mutual Fund with quantity',
		response_obj['status'] = add_or_update_mutual_fund(client,get_holding(entry,item['itemDisplayName']))

	else:
				
		response_obj['type_of_asset'] = 'Stock',
		response_obj['status'] = add_or_update_stock(client,get_holding(entry,item['itemDisplayName']))

	return response_obj
						

def process_yodlee_holding_item(client,item,index):

	mapping_status = []

	holding_item = item['itemData']['accounts'][index]['holdings']

	for i,entry in enumerate(holding_item):

		if entry['holdingType'] == 'mutualFund':

			mapping_status.append(process_yodlee_mutual_fund(client,entry,item))

		elif entry['holdingType'] == 'stock':

			mapping_status.append(process_yodlee_stock(client,entry,item))
	
	return mapping_status

def process_yodlee_item(client,item):

	mapping_status = []

	if 'itemData' in item:

		for index in range(len(item['itemData']['accounts'])):

			if 'availableBalance' in item['itemData']['accounts'][index]:

				mapping_status.append({
						'type_of_asset': 'Savings Account',
						'status': add_or_update_other_investment(client,get_bank_account(item,index,'Savings Account'))
						})

			elif 'maturityAmount' in item['itemData']['accounts'][index]:

				mapping_status.append({
						'type_of_asset': 'Deposits',
						'status': add_or_update_other_investment(client,get_bank_account(item,index,'Deposits'))
						})

			elif 'holdings' in item['itemData']['accounts'][index]:

				mapping_status += process_yodlee_holding_item(client,item,index)
	
	return mapping_status