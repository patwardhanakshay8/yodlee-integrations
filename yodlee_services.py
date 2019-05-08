# Yodlee Services

from django.conf import settings
from portfolio.models import *
import requests


def cobrand_login():

	payload = { "cobrandLogin":settings.COBRAND_USERNAME, "cobrandPassword":settings.COBRAND_PASSWORD }
	
	response = requests.post('https://sdkint11.yodlee.com/yodsoap/srest/sacredcapital/v1.0/authenticate/coblogin/', params=payload).json()
	
	return response['cobrandConversationCredentials']['sessionToken']

def register_user(cobrand_session_token,user_login,user_password):

	payload = { "cobSessionToken" : cobrand_session_token ,"userCredentials.loginName" : user_login ,"userCredentials.password" : user_password ,"userCredentials.objectInstanceType":"com.yodlee.ext.login.PasswordCredentials" ,"userProfile.emailAddress" : user_login }
	
	response = requests.post('https://sdkint11.yodlee.com/yodsoap/srest/sacredcapital/v1.0/jsonsdk/UserRegistration/register3/', params=payload).json()

	return response

def reset_password(cobrand_session_token,user_login,user_password):

	step_one_token = ''
	step_two_token = ''

	payload = { "cobSessionToken" : cobrand_session_token ,"username" : user_login }
	response = requests.post('https://sdkint11.yodlee.com/yodsoap/srest/sacredcapital/v1.0/jsonsdk/PasswordResetManagement/getToken/', params=payload).json()
	
	step_one_token = response['token']

	payload = { "cobSessionToken" : cobrand_session_token ,"token" : step_one_token }
	response = requests.post('https://sdkint11.yodlee.com/yodsoap/srest/sacredcapital/v1.0/jsonsdk/PasswordResetManagement/getPasswordResetUserContextFromToken/', params=payload).json()
			
	step_two_token = response['conversationCredentials']['sessionToken']

	payload = { "cobSessionToken" : cobrand_session_token ,"token" : step_one_token ,"userSessionToken" : step_two_token }
	response = requests.post('https://sdkint11.yodlee.com/yodsoap/srest/sacredcapital/v1.0/jsonsdk/PasswordResetManagement/setSessionForValidToken/', params=payload).json()
			
	payload = { "cobSessionToken" : cobrand_session_token ,"token" : step_one_token ,"userSessionToken" : step_two_token ,"newCredentials.objectInstanceType" : "com.yodlee.ext.login.PasswordCredentials" , "newCredentials.password" : user_password }
	response = requests.post('https://sdkint11.yodlee.com/yodsoap/srest/sacredcapital/v1.0/jsonsdk/PasswordResetManagement/changePassword/', params=payload).json()
	
	return response

	
def user_login(cobrand_session_token,user_login,user_password):

	client = Client.objects.get(client__username=user_login)

	if client.yodlee_login and client.yodlee_password:

		payload = { "cobSessionToken" : cobrand_session_token, "login":client.yodlee_login, "password":client.yodlee_password }

	else:

		payload = { "cobSessionToken" : cobrand_session_token, "login":user_login, "password":user_password }

	response = requests.post('https://sdkint11.yodlee.com/yodsoap/srest/sacredcapital/v1.0/authenticate/login/', params=payload).json()

	if 'userContext' in response:
		response = response['userContext']['conversationCredentials']['sessionToken']
	elif 'Error' in response:
		response = response['Error'][0]['errorDetail']

	return response

def get_account_item_list(cobrand_session_token,user_session_token):

	item_ids = []

	payload = { "cobSessionToken" : cobrand_session_token, "userSessionToken" : user_session_token }
	
	response = requests.post('https://sdkint11.yodlee.com/yodsoap/srest/sacredcapital/v1.0/jsonsdk/DataService/getItemSummariesWithoutItemData/', params=payload).json()

	response_string = " ".join(str(x) for x in response)

	if 'itemId' in response_string:
		for i,entry in enumerate(response):
			item_ids.append(entry['itemId'])
	
	return item_ids

def get_individual_item(cobrand_session_token,user_session_token,item_id):

	payload = { "cobSessionToken" : cobrand_session_token ,"userSessionToken" : user_session_token ,"itemId" : item_id ,"dex.startLevel" : "0" ,"dex.endLevel" : "2", "dex.extentLevels[0]" : "0" ,"dex.extentLevels[1]" : "2" }

	response = requests.post('https://sdkint11.yodlee.com/yodsoap/srest/sacredcapital/v1.0/jsonsdk/DataService/getItemSummaryForItem1/', params=payload).json()

	return response

def get_fastlink_credentials(cobrand_session_token,user_session_token):

	payload = { "cobSessionToken" : cobrand_session_token ,"rsession" : user_session_token ,"finAppId" : settings.APP_ID }

	response = requests.post('https://sdkint11.yodlee.com/yodsoap/srest/sacredcapital/v1.0/authenticator/token/', params=payload).json()

	return response['finappAuthenticationInfos'][0]['token']

# Savings Account or Fixed Deposits
def get_bank_account(yodlee_response_item,item_array_index,type_of_investment):

	values = {}
	if type_of_investment == 'Savings Account':
		values['type_of_investment'] = type_of_investment
		values['value'] = yodlee_response_item['itemData']['accounts'][item_array_index]['availableBalance']['amount']
		values['currency'] = yodlee_response_item['itemData']['accounts'][item_array_index]['availableBalance']['currencyCode']
	elif type_of_investment == 'Deposits':
		values['type_of_investment'] = type_of_investment
		values['value'] = yodlee_response_item['itemData']['accounts'][item_array_index]['maturityAmount']['amount']
		values['currency'] = yodlee_response_item['itemData']['accounts'][item_array_index]['maturityAmount']['currencyCode']
	values['description'] = yodlee_response_item['itemDisplayName']
	values['source'] = yodlee_response_item['itemDisplayName']
	values['holding_id'] = yodlee_response_item['itemData']['accounts'][item_array_index]['accountId']
	
	return values
	
# Gold
def get_other_investment_holding(yodlee_holding_item,source,type_of_investment):

	values = {}
	values['type_of_investment'] = type_of_investment
	values['description'] = yodlee_holding_item['description']
	values['source'] = source
	values['holding_id'] = yodlee_holding_item['holdingId']
	values['currency'] = yodlee_holding_item['value']['currencyCode']
	values['value'] = yodlee_holding_item['value']['amount']

	return values

# Mutual Fund with or without quantity, Stock, Bond
def get_holding(yodlee_holding_item,source):

	values = {}
	values['title'] = yodlee_holding_item['description']
	values['source'] = source
	values['holding_id'] = yodlee_holding_item['holdingId']

	if 'quantity' in yodlee_holding_item:
		values['quantity'] = yodlee_holding_item['quantity']
	else:
		values['quantity'] = 0.0

	if 'price' in yodlee_holding_item: 
		values['currency'] = yodlee_holding_item['price']['currencyCode']
	else:
		values['currency'] = 'INR'

	if 'price' in yodlee_holding_item:
		values['price'] = yodlee_holding_item['price']['amount']
	else:
		values['price'] = 0.0
		
 	values['value'] = yodlee_holding_item['value']['amount']

	return values
	






