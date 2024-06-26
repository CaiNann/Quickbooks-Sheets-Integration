from intuitlib.client import AuthClient
from intuitlib.enums import Scopes
from google.oauth2 import service_account
import googleapiclient.discovery
import requests
import http.server
import socketserver
import hashlib, hmac, base64
from urllib.parse import urlparse, parse_qs, urlencode
import secrets
import config
import json

googleCredentials = service_account.Credentials.from_service_account_file(config.google['service_account_file'], scopes=config.google['scopes'])
sheetsService = googleapiclient.discovery.build('sheets', 'v4', credentials=googleCredentials)
auth = base64.b64encode(f"{config.quickbooks['client_id']}:{config.quickbooks['client_secret']}".encode()).decode('utf-8')


class RequestHandler(http.server.BaseHTTPRequestHandler):
    session = {}

    def do_GET(self):
        parsed_url = urlparse(self.path)
        query_components = parse_qs(urlparse(self.path).query)
        if parsed_url.path == '/authUri':
            state = secrets.token_urlsafe(16)
            self.server.csrf_state = state
            params = {
                'client_id': config.quickbooks['client_id'],
                'redirect_uri': config.quickbooks['redirect_uri'],
                'scope': config.quickbooks['scopes'][0],
                'response_type': 'code',
                'state': state,
            }
            auth_url = f'{config.quickbooks['authorization_endpoint']}?{urlencode(params)}'
            
            self.send_response(302)
            self.send_header('Location', auth_url)
            self.end_headers()

        elif parsed_url.path == '/callback':
            if self.server.csrf_state != query_components.get('state', [''])[0]:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'CSRF Token mismatch')
                return
            config.quickbooks['realm_id'] = query_components.get('realmId', [''])[0]
            code = query_components.get('code', [''])[0]

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

            response = requests.post(post_body['url'], headers=post_body['headers'], data=post_body['data'])

            if response.status_code == 200:
                self.session['access_token'] = response.json().get('access_token')
                self.session['refresh_token'] = response.json().get('refresh_token')
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
            else:
                self.send_response(500)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(f"Error: Token request failed [{response.status_code}]".encode())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')
            print(f"Path {self.path} not found")
    def do_POST(self):
        parsed_url = urlparse(self.path)
        content_length = int(self.headers['content-length'])
        body = self.rfile.read(content_length)
        payload = json.loads(body.decode('utf-8'))
        if parsed_url.path == '/webhook':
            signature = self.headers['intuit-signature']
            if isValidPayload(signature, body):
                self.send_response(200, 'Payload is valid')
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                event_notifications = payload['eventNotifications']
                for notification in event_notifications:
                    data_change_event = notification['dataChangeEvent']
                    entities = data_change_event['entities']
                    for entity in entities:
                        operation = entity['operation']
                        estimate_id = entity['id']
                        if operation == 'Delete':
                            #deleteEstimate(deleted_id)
                            print(f'Deleted Estimate ID: {estimate_id}'.encode())
                        elif operation == 'Create':
                            access_token = self.session.get('access_token')
                            getEstimateData(estimate_id, access_token)
                            #appendSheet('1fRHggwg7dhvj7447InWxbL2qY7mQLcys13e0iTN2E0s', 'Open Order Report', )
                        elif operation == 'Update':
                            #updateEstimate(estimate_id)
                            print(f'Updated Estimate ID: {estimate_id}'.encode())
                    
def refresh_token(refresh_token):
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

def isValidPayload(signature, payload):
    key = config.quickbooks['webhooks_verifier']
    key_to_verify = key.encode('ascii')
    hashed = hmac.new(key_to_verify, payload, hashlib.sha256).digest()
    hashed_base64 = base64.b64encode(hashed).decode()

    if signature == hashed_base64:
        return True
    return False

def getEstimateData(id, auth_token, refresh_token):
    url = f'{config.quickbooks['sandbox_base_url']}/v3/company/{config.quickbooks['realm_id']}/{id}?minorversion=70'
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {auth_token}',
    }
    try:
        response = requests.get(url, headers)
        response.raise_for_status()
        data = response.json()
        print(data)
    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 401:
            new_token = refresh_token(refresh_token)
            if new_token:
                self.session['access_token'] = new_token
                headers['Authorization'] = f'Bearer {new_token}'
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()
                print(data)
            else:
                print("Failed to refresh token.")
        else:
            print(f"HTTP error occurred: {http_err}")
            print(f"Response status code: {response.status_code}")
            print(f"Response content: {response.content}")
    except json.JSONDecodeError as json_err:
        print(f"JSONDeocdeError: {json_err}")
        print("Response content:", response.content)

def getSheetValues(id, range):
    sheet_values = sheetsService.spreadsheets().values().get(spreadsheetId=id, range=range).execute()
    return sheet_values

def appendSheet(id, range, values):
    sheet_response = sheetsService.spreadsheets().values().append(spreadsheetId=id, range=range, values=values).execute()
    return sheet_response

def start_server():
    server_address = ('localhost', 9000)
    httpd = socketserver.TCPServer(server_address, RequestHandler)
    print(f"Server running on port {server_address[1]}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\nStopping server...')
        httpd.server_close()

if __name__ == '__main__':
    start_server()