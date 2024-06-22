from intuitlib.client import AuthClient
from intuitlib.enums import Scopes
import requests
import http.server
import socketserver
import base64
from urllib.parse import urlparse, parse_qs, urlencode
import secrets

client_id = 'ABELy2kJPVjKIaWycZKD8B9rF1fPLpMyxq5Y5zhgOY8jd5l4Fj'
client_secret = '05EYhumz1oXvKQqiCOVsVYhCvUZ2OV4Pi688esWL'
redirect_uri = 'https://0ae3-76-170-113-56.ngrok-free.app/callback'
environment = 'sandbox'
token_endpoint = 'https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer'
authorization_endpoint = 'https://appcenter.intuit.com/connect/oauth2'
realm_id = '9341452557106265'

scopes = [
    "com.intuit.quickbooks.accounting"
]

class RequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        query_components = parse_qs(urlparse(self.path).query)
        if parsed_url.path == '/authUri':
            state = secrets.token_urlsafe(16)
            self.server.csrf_state = state
            params = {
                'client_id': client_id,
                'redirect_uri': redirect_uri,
                'scope': scopes[0],
                'response_type': 'code',
                'state': state,
            }
            auth_url = f'{authorization_endpoint}?{urlencode(params)}'
            
            self.send_response(302)
            self.send_header('Location', auth_url)
            self.end_headers()

        elif parsed_url.path == '/callback':
            if self.server.csrf_state != query_components.get('state', [''])[0]:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'CSRF Token mismatch')
                return
            realm_id = query_components.get('realmId', [''])[0]
            code = query_components.get('code', [''])[0]

            auth = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode('utf-8')
            print(auth)
            post_body = {
                'url': token_endpoint,
                'headers': {
                    'Accept': 'application/json',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Authorization': f'Basic {auth}',
                },
                'data': {
                    'grant_type': 'authorization_code',
                    'code': code,
                    'redirect_uri': redirect_uri,
                }
            }

            response = requests.post(post_body['url'], headers=post_body['headers'], data=post_body['data'])

            if response.status_code == 200:
                access_token = response.json().get('access_token')
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(f"Access Token: {access_token}".encode())
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