import http.server
import socketserver
from urllib.parse import urlparse, parse_qs
import secrets
import config
from quickbooks_functions import *
from google_functions import *
import json

class RequestHandler(http.server.BaseHTTPRequestHandler):
    session = {}

    def do_GET(self):
        parsed_url = urlparse(self.path)
        query_components = parse_qs(urlparse(self.path).query)
        if parsed_url.path == '/authUri':
            state = secrets.token_urlsafe(16)
            self.server.csrf_state = state
            auth_url = authenticate(state)
            self.send_response(302)
            self.send_header('Location', auth_url)
            self.end_headers()
        elif parsed_url.path == '/callback':
            if self.server.csrf_state != query_components.get('state', [''])[0]:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'CSRF Token mismatch')
                return
            code = query_components.get('code', [''])[0]
            response = authorize(code)
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
            if is_valid_payload(signature, body):
                self.send_response(200, 'Payload is valid')
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                access_token = self.session.get('access_token')
                refresh_token = self.session.get('refresh_token')
                entities = parse_payload(payload)
                for entity in entities:
                    print(entity['lastUpdated'])
                    operation = entity['operation']
                    estimate_id = entity['id']
                    estimate_data = get_estimate_data(estimate_id, access_token, refresh_token)
                    if operation == 'Delete':
                        print(f'Deleted Estimate ID: {estimate_id}'.encode())
                    elif operation == 'Create':
                        append_sheet(config.google['spreadsheet_id'], config.google['append_table_range'], estimate_data)
                    elif operation == 'Update':
                        purchase_order_num = estimate_data[3]
                        print(purchase_order_num)
                        update_sheet(config.google['spreadsheet_id'], purchase_order_num, estimate_data)

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