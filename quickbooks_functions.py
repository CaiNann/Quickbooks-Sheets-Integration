import config
from urllib.parse import urlencode
import hashlib, hmac, base64
import requests
from util import *
from dynamodb_functions import *
import time

MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 1

auth = base64.b64encode(f"{config.quickbooks['client_id']}:{config.quickbooks['client_secret']}".encode()).decode('utf-8')

def authenticate(state):
    params = {
        'client_id': config.quickbooks['client_id'],
        'redirect_uri': config.quickbooks['redirect_uri'],
        'scope': config.quickbooks['scopes'][0],
        'response_type': 'code',
        'state': state,
    }
    auth_url = f'{config.quickbooks['authorization_endpoint']}?{urlencode(params)}'
    return auth_url

def authorize(code, user_id, realm_id):
    post_body = {
        'url': config.quickbooks['token_endpoint'],
        'headers': {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Basic {auth}',
        },
        'data': {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': config.quickbooks['redirect_uri'],
        }
    }

    retries = 0

    while retries < MAX_RETRIES:
        response = requests.post(post_body['url'], headers=post_body['headers'], data=post_body['data'])
        if response.status_code == 200:
            delete_state_from_dynamodb(user_id)
            access_token = response.json().get('access_token')
            refresh_token = response.json().get('refresh_token')
            save_tokens_to_dynamodb(realm_id, access_token, refresh_token)
            return {
                'statusCode': 200,
                'body': 'Tokens successfully received'
            }
        else:
            retries += 1
            if retries < MAX_RETRIES:
                time.sleep(RETRY_DELAY_SECONDS)
            else:
                return {
                    'statusCode': 500,
                    'body': f"Error: Token request failed [{response.status_code}]"
                }

def refresh_auth_token(refresh_token):
    post_body = {
        'url': config.quickbooks['token_endpoint'],
        'headers': {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Basic {auth}',
        },
        'data': {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
        }
    }
    response = requests.post(post_body['url'], headers=post_body['headers'], data=post_body['data'])
    response.raise_for_status()
    data = response.json()
    return data.get('access_token')

def is_valid_payload(signature, payload):
    key = config.quickbooks['webhooks_verifier']
    key_to_verify = key.encode('utf-8')
    payload_bytes = payload.encode('utf-8')
    hashed = hmac.new(key_to_verify, payload_bytes, hashlib.sha256).digest()
    hashed_base64 = base64.b64encode(hashed).decode()

    if signature == hashed_base64:
        return True
    return False

def get_estimate_data(estimate_id, auth_token, refresh_token, realm_id):
    url = f'{config.quickbooks['production_base_url']}/v3/company/{realm_id}/estimate/{estimate_id}'
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {auth_token}',
    }
    try:
        response = requests.get(url, headers)
        response.raise_for_status()
        data = response.json()
        sales_order_num = data.get('Estimate').get('CustomField')[1].get('StringValue')
        if sales_order_num == None:
            sales_order_num = ' '
        date = data.get('Estimate').get('MetaData').get('CreateTime')
        date = format_date(date)
        customer = data.get('Estimate').get('CustomerRef').get('name')
        purchase_order_num = data.get('Estimate').get('CustomField')[0].get('StringValue')
        if purchase_order_num == None:
            purchase_order_num = ' '
        description = []
        items = data.get('Estimate').get('Line')
        for item in items:
            if item.get('Description') != None:
                description.append(item.get('Description'))
        if len(description) != 0:
            description = ', '.join(description)
        filteredData = [estimate_id, sales_order_num, date, customer, purchase_order_num, description]
        return filteredData
    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 401:
            new_token = refresh_auth_token(refresh_token)
            if new_token:
                save_tokens_to_dynamodb(realm_id, new_token, refresh_token)
                headers['Authorization'] = f'Bearer {new_token}'
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()
                sales_order_num = data.get('Estimate').get('CustomField')[1].get('StringValue')
                if sales_order_num == None:
                    sales_order_num = ' '
                date = data.get('Estimate').get('MetaData').get('CreateTime')
                date = format_date(date)
                customer = data.get('Estimate').get('CustomerRef').get('name')
                purchase_order_num = data.get('Estimate').get('CustomField')[0].get('StringValue')
                if purchase_order_num == None:
                    purchase_order_num = ' '
                description = []
                items = data.get('Estimate').get('Line')
                for item in items:
                    if item.get('Description') != None:
                        description.append(item.get('Description'))
                if len(description) != 0:
                    description = ', '.join(description)
                filteredData = [estimate_id, sales_order_num, date, customer, purchase_order_num, description]
                return filteredData
            else:
                print("Failed to refresh token.")
        else:
            print(f"HTTP error occurred: {http_err}")
            print(f"Response status code: {response.status_code}")
            print(f"Response content: {response.content}")