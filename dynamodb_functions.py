import boto3

dynamodb = boto3.client('dynamodb')
table_name = 'quickbooks_auth_tokens'

def save_state_to_dynamodb(user_id, state):
    try:
        response = dynamodb.put_item(
            TableName=table_name,
            Item={
                'UserId': {'S': user_id},
                'State': {'S': state}
            }
        )
        print(f"Saved state {state} for user {user_id} to DynamoDB")
    except Exception as e:
        print(f"Error saving state to DynamoDB: {str(e)}")

def save_tokens_to_dynamodb(user_id, access_token, refresh_token):
    try:
        response = dynamodb.put_item(
            TableName=table_name,
            Item={
                'UserId': {'S': user_id},
                'AccessToken': {'S': access_token},
                'RefreshToken': {'S': refresh_token}
            }
        )
        print(f"Saved tokens for user {user_id} to DynamoDB")
    except Exception as e:
        print(f"Error saving tokens to DynamoDB: {str(e)}")

def get_access_token_from_dynamodb(user_id):
    try:
        response = dynamodb.get_item(
            TableName=table_name,
            Key={
                'UserId': {'S': user_id}
            }
        )
        if 'Item' in response:
            return response['Item'].get('AccessToken', {}).get('S', '')
        else:
            return None
    except Exception as e:
        print(f"Error getting access token from DynamoDB: {str(e)}")
        return None

def get_refresh_token_from_dynamodb(user_id):
    try:
        response = dynamodb.get_item(
            TableName=table_name,
            Key={
                'UserId': {'S': user_id}
            }
        )
        if 'Item' in response:
            return response['Item'].get('RefreshToken', {}).get('S', '')
        else:
            return None
    except Exception as e:
        print(f"Error getting refresh token from DynamoDB: {str(e)}")
        return None