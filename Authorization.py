from intuitlib.client import AuthClient
from intuitlib.enums import Scopes
import ngrok
import requests
import http.server
import base64
from urllib.parse import urlparse, parse_qs, quote

listener = ngrok.forward(9000, authtoken_from_env=True)
print(f"Ingress established at {listener.url()}")

client_id = 'ABELy2kJPVjKIaWycZKD8B9rF1fPLpMyxq5Y5zhgOY8jd5l4Fj'
client_secret = '05EYhumz1oXvKQqiCOVsVYhCvUZ2OV4Pi688esWL'
redirect_uri = 'https://db70-45-48-118-32.ngrok-free.app/callback'
environment = 'sandbox'
token_endpoint = 'https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer'
authorization_endpoint = 'https://appcenter.intuit.com/connect/oauth2'
realm_id = '9341452557106265'

auth_client = AuthClient(client_id, client_secret, redirect_uri, environment)

scopes = [
    Scopes.ACCOUNTING
]

auth_url = auth_client.get_authorization_url(scopes)
print(auth_url)
class RequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        query_components = parse_qs(urlparse(self.path).query)
        if parsed_url.path == '/authUri':
            redirectUrl = '%s
            ?client_id=%s
            &redirect_uri=%s
            &scope={scopes[0]}
            &response_type=code'
            self.wfile.write(redirectUrl)

        if parsed_url.path == '/callback':
            realm_id = query_components.get('realmId', [''])[0]
            code = query_components.get('code', [''])[0]

            auth = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode('utf-8')

            post_body = {
                'url': token_endpoint,
                'headers': {
                    'Accept': 'application/json',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Authorization': f'Basic {auth}',
                },
                'data': {
                    'grant_type': 'authorization_code',
                    'code': query_components.get('code', [''])[0],
                    'redirect_uri': redirect_uri
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

def start_server():
    server_address = ('', 9000)  # Choose a port number
    httpd = http.server.HTTPServer(server_address, RequestHandler)
    print(f"Server running on port {server_address[1]}")
    httpd.serve_forever()

if __name__ == '__main__':
    start_server()