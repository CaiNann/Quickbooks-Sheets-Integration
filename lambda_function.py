import secrets
import config
from dynamodb_functions import *
from quickbooks_functions import *
from google_functions import *
import json

def lambda_handler(event, context):
    path = event['path']
    user_id = event['requestContext']['accountId']
    print(json.dumps(event))
    print(context)
    if path == '/authUri':
        state = secrets.token_urlsafe(16)
        save_state_to_dynamodb(user_id, state)
        auth_url = authenticate(state)
        return {
            'statusCode': 302,
            'headers': {
                'Location': auth_url
        }
    }
    
    if path == '/callback':
        query_params = event['queryStringParameters']
        if get_state_from_dynamodb(user_id) != query_params.get('state', ''):
            return {
                'statusCode': 400,
                'body': 'CSRF Token mismatch'
            }
        
        code = query_params.get('code', '')
        response = authorize(code)
        
        if response.status_code == 200:
            access_token = response.json().get('access_token')
            refresh_token = response.json().get('refresh_token')
            save_tokens_to_dynamodb(user_id, access_token, refresh_token)
            return {
                'statusCode': 200,
                'body': json.dumps(response.json())
            }
        else:
            return {
                'statusCode': 500,
                'body': f"Error: Token request failed [{response.status_code}]"
            }
    
    elif path == '/webhook':
        signature = event['headers']['intuit-signature']
        body = event['body']
        if is_valid_payload(signature, body):
            access_token = get_access_token_from_dynamodb(user_id)
            refresh_token = get_refresh_token_from_dynamodb(user_id)
            
            entities = parse_payload(json.loads(body))
            for entity in entities:
                operation = entity['operation']
                estimate_id = entity['id']
                
                if operation == 'Delete':
                    delete_row(config.google['spreadsheet_id'], estimate_id)
                else:
                    estimate_data = get_estimate_data(estimate_id, access_token, refresh_token, user_id)
                    if operation == 'Create':
                        append_row(config.google['spreadsheet_id'], estimate_data)
                    elif operation == 'Update':
                        update_row(config.google['spreadsheet_id'], estimate_id, estimate_data)
            
            return {
                'statusCode': 200,
                'body': 'Payload processed successfully'
            }
        else:
            return {
                'statusCode': 403,
                'body': 'Invalid payload signature'
            }
    
    else:
        return {
            'statusCode': 404,
            'body': 'Not Found'
        }