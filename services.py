from intuitlib.client import AuthClient
from intuitlib.enums import Scopes
import requests
import http.server
import socketserver
import hashlib, hmac, base64
from urllib.parse import urlparse, parse_qs, urlencode
import secrets
import config
import json

class RequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        query_components = parse_qs(urlparse(self.path).query)
        if parsed_url.path == '/authUri':
            state = secrets.token_urlsafe(16)
            self.server.csrf_state = state
            params = {
                'client_id': config.client_id,
                'redirect_uri': config.redirect_uri,
                'scope': config.scopes[0],
                'response_type': 'code',
                'state': state,
            }
            auth_url = f'{config.authorization_endpoint}?{urlencode(params)}'
            
            self.send_response(302)
            self.send_header('Location', auth_url)
            self.end_headers()

        elif parsed_url.path == '/callback':
            if self.server.csrf_state != query_components.get('state', [''])[0]:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'CSRF Token mismatch')
                return
            config.realm_id = query_components.get('realmId', [''])[0]
            code = query_components.get('code', [''])[0]

            auth = base64.b64encode(f"{config.client_id}:{config.client_secret}".encode()).decode('utf-8')
            print(auth)
            post_body = {
                'url': config.token_endpoint,
                'headers': {
                    'Accept': 'application/json',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Authorization': f'Basic {auth}',
                },
                'data': {
                    'grant_type': 'authorization_code',
                    'code': code,
                    'redirect_uri': config.redirect_uri,
                }
            }

            response = requests.post(post_body['url'], headers=post_body['headers'], data=post_body['data'])

            if response.status_code == 200:
                access_token = response.json().get('access_token')
                refresh_token = response.json().get('refresh_token')
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(f"Access Token: {access_token}\n\n".encode())
                self.wfile.write(f'Refresh Token: {refresh_token}'.encode())
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
                            #createEstimate(estimate_id)
                            print(f'Created Estimate ID: {estimate_id}'.encode())
                        elif operation == 'Update':
                            #updateEstimate(estimate_id)
                            print(f'Updated Estimate ID: {estimate_id}'.encode())
                    

def isValidPayload(signature, payload):
    key = config.webhooks_verifier
    key_to_verify = key.encode('ascii')
    hashed = hmac.new(key_to_verify, payload, hashlib.sha256).digest()
    hashed_base64 = base64.b64encode(hashed).decode()

    if signature == hashed_base64:
        return True
    return False

#def deleteEstimate(id):
    super.wfile.write(f'Deleted Estimate ID: {id}'.encode())

#def createEstimate(id):
    super.wfile.write(f'Created Estimate ID: {id}'.encode())

#def updateEstimate(id):
    super.wfile.write(f'Updated Estimate ID: {id}'.encode())

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