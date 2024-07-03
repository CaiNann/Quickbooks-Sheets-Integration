import secrets
import config
from dynamodb_functions import *
from quickbooks_functions import *
from google_functions import *
import json

def lambda_handler(event, context):
    path = event['path']
    query_params = event['queryStringParameters'] if 'queryStringParameters' in event else {}
    body = event['body'] if 'body' in event else None
    
    if path == '/authUri':
        state = secrets.token_urlsafe(16)
        save_state_to_dynamodb(context.session['userId'], state)
        auth_url = authenticate(state)
        return {
            'statusCode': 302,
            'headers': {
                'Location': auth_url
            }
        }
    
    elif path == '/callback':
        if context.csrf_state != query_params.get('state', ''):
            return {
                'statusCode': 400,
                'body': 'CSRF Token mismatch'
            }
        
        code = query_params.get('code', '')
        response = authorize(code)
        
        if response.status_code == 200:
            access_token = response.json().get('access_token')
            refresh_token = response.json().get('refresh_token')
            save_tokens_to_dynamodb(context.session['userId'], access_token, refresh_token)
            return {
                'statusCode': 200,
                'body': json.dumps(response)
            }
        else:
            return {
                'statusCode': 500,
                'body': f"Error: Token request failed [{response.status_code}]"
            }
    
    elif path == '/webhook' and event['httpMethod'] == 'POST':
        signature = event['headers']['intuit-signature']
        if is_valid_payload(signature, body):
            access_token = get_access_token_from_dynamodb(context.session['userId'])
            refresh_token = get_refresh_token_from_dynamodb(context.session['userId'])
            
            entities = parse_payload(json.loads(body))
            for entity in entities:
                operation = entity['operation']
                estimate_id = entity['id']
                
                if operation == 'Delete':
                    delete_row(config.google['spreadsheet_id'], estimate_id)
                else:
                    estimate_data = get_estimate_data(estimate_id, access_token, refresh_token, context.session['userId'])
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