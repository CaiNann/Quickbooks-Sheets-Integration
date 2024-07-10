import boto3

dynamodb = boto3.client('dynamodb')
table_name = 'quickbooks_info'

def save_state_to_dynamodb(realm_id, state):
    try:
        response = dynamodb.put_item(
            TableName=table_name,
            Item={
                'realmId': {'S': realm_id},
                'State': {'S': state}
            }
        )
        print(f"Saved state {state} for user {realm_id} to DynamoDB")
    except Exception as e:
        print(f"Error saving state to DynamoDB: {str(e)}")

def delete_state_from_dynamodb(account_id):
    try:
        response = dynamodb.delete_item(
            TableName=table_name,
            Key={
                'realmId': {'S': account_id},
            }
        )
        print(f"Deleted state from DynamoDB")
    except Exception as e:
        print(f"Error deleting state from DynamoDB: {str(e)}")

def delete_company_from_dynamodb(realm_id):
    try:
        response = dynamodb.delete_item(
            TableName=table_name,
            Key={
                'realmId': {'S': realm_id},
            }
        )
        print(f"Deleted company from DynamoDB")
        return response
    except Exception as e:
        print(f"Error deleting company from DynamoDB: {str(e)}")
        return response

def save_tokens_to_dynamodb(realm_id, access_token, refresh_token):
    try:
        response = dynamodb.put_item(
            TableName=table_name,
            Item={
                'realmId': {'S': realm_id},
                'AccessToken': {'S': access_token},
                'RefreshToken': {'S': refresh_token}
            }
        )
        print(f"Saved tokens for comapny {realm_id} to DynamoDB")
        return response
    except Exception as e:
        print(f"Error saving tokens to DynamoDB: {str(e)}")
        return response

def get_state_from_dynamodb(realm_id):
    try:
        response = dynamodb.get_item(
            TableName=table_name,
            Key={
                'realmId': {'S': realm_id}
            }
        )
        if 'Item' in response:
            return response['Item'].get('State', {}).get('S', '')
        else:
            return None
    except Exception as e:
        print(f"Error getting state from DynamoDB: {str(e)}")
        return None

def get_access_token_from_dynamodb(realm_id):
    try:
        response = dynamodb.get_item(
            TableName=table_name,
            Key={
                'realmId': {'S': realm_id}
            }
        )
        if 'Item' in response:
            return response['Item'].get('AccessToken', {}).get('S', '')
        else:
            return None
    except Exception as e:
        print(f"Error getting access token from DynamoDB: {str(e)}")
        return None

def get_refresh_token_from_dynamodb(realm_id):
    try:
        response = dynamodb.get_item(
            TableName=table_name,
            Key={
                'realmId': {'S': realm_id}
            }
        )
        if 'Item' in response:
            return response['Item'].get('RefreshToken', {}).get('S', '')
        else:
            return None
    except Exception as e:
        print(f"Error getting refresh token from DynamoDB: {str(e)}")
        return None