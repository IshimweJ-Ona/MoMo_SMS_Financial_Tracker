from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import base64
from datetime import datetime

# Sample user database
USERS = {
    "admin": "password123",
    "user": "user123"
}

# Import our data parser
from data_parser import SMSDataParser

class TransactionAPIHandler(BaseHTTPRequestHandler):
    
    def _set_headers(self, status_code=200, content_type='application/json'):
        """Set HTTP headers"""
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def do_OPTIONS(self):
        """Handle OPTIONS for CORS"""
        self._set_headers(200)
    
    def authenticate(self):
        """Basic Authentication"""
        auth_header = self.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Basic '):
            return False
        
        # Decode credentials
        auth_decoded = base64.b64decode(auth_header[6:]).decode('utf-8')
        username, password = auth_decoded.split(':', 1)
        
        return USERS.get(username) == password
    
    def parse_path(self):
        """Parse request path and extract ID if present"""
        path_parts = self.path.split('/')
        if len(path_parts) > 2 and path_parts[1] == 'transactions':
            if path_parts[2].isdigit():
                return int(path_parts[2])
        return None
    
    def get_request_body(self):
        """Get and parse request body"""
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > 0:
            body = self.rfile.read(content_length)
            return json.loads(body.decode('utf-8'))
        return {}
    
    # CRUD Operations
    def do_GET(self):
        """Handle GET requests"""
        if not self.authenticate():
            self._set_headers(401)
            self.wfile.write(json.dumps({'error': 'Unauthorized'}).encode())
            return
        
        transaction_id = self.parse_path()
        
        if transaction_id is not None:
            # GET /transactions/{id}
            transaction = self.server.transactions_dict.get(transaction_id)
            if transaction:
                self._set_headers(200)
                self.wfile.write(json.dumps(transaction).encode())
            else:
                self._set_headers(404)
                self.wfile.write(json.dumps({'error': 'Transaction not found'}).encode())
        else:
            # GET /transactions
            self._set_headers(200)
            self.wfile.write(json.dumps(self.server.transactions).encode())
    
    def do_POST(self):
        """Handle POST requests"""
        if not self.authenticate():
            self._set_headers(401)
            self.wfile.write(json.dumps({'error': 'Unauthorized'}).encode())
            return
        
        if self.path == '/transactions':
            try:
                body = self.get_request_body()
                
                # Generate new ID
                new_id = max([txn['id'] for txn in self.server.transactions]) + 1 if self.server.transactions else 1
                body['id'] = new_id
                
                # Add timestamp if not provided
                if 'timestamp' not in body:
                    body['timestamp'] = datetime.now().isoformat()
                
                self.server.transactions.append(body)
                self.server.transactions_dict[new_id] = body
                
                self._set_headers(201)
                self.wfile.write(json.dumps(body).encode())
            except Exception as e:
                self._set_headers(400)
                self.wfile.write(json.dumps({'error': str(e)}).encode())
    
    def do_PUT(self):
        """Handle PUT requests"""
        if not self.authenticate():
            self._set_headers(401)
            self.wfile.write(json.dumps({'error': 'Unauthorized'}).encode())
            return
        
        transaction_id = self.parse_path()
        if transaction_id is not None:
            transaction = self.server.transactions_dict.get(transaction_id)
            if transaction:
                try:
                    body = self.get_request_body()
                    body['id'] = transaction_id  # Ensure ID consistency
                    
                    # Update transaction
                    index = next(i for i, t in enumerate(self.server.transactions) if t['id'] == transaction_id)
                    self.server.transactions[index] = body
                    self.server.transactions_dict[transaction_id] = body
                    
                    self._set_headers(200)
                    self.wfile.write(json.dumps(body).encode())
                except Exception as e:
                    self._set_headers(400)
                    self.wfile.write(json.dumps({'error': str(e)}).encode())
            else:
                self._set_headers(404)
                self.wfile.write(json.dumps({'error': 'Transaction not found'}).encode())
    
    def do_DELETE(self):
        """Handle DELETE requests"""
        if not self.authenticate():
            self._set_headers(401)
            self.wfile.write(json.dumps({'error': 'Unauthorized'}).encode())
            return
        
        transaction_id = self.parse_path()
        if transaction_id is not None:
            transaction = self.server.transactions_dict.get(transaction_id)
            if transaction:
                self.server.transactions = [t for t in self.server.transactions if t['id'] != transaction_id]
                if transaction_id in self.server.transactions_dict:
                    del self.server.transactions_dict[transaction_id]
                
                self._set_headers(200)
                self.wfile.write(json.dumps({'message': 'Transaction deleted'}).encode())
            else:
                self._set_headers(404)
                self.wfile.write(json.dumps({'error': 'Transaction not found'}).encode())

def run_server(port=8000):
    """Start the HTTP server"""
    # Parse data first
    print("Parsing SMS data...")
    parser = SMSDataParser('modified_sms_v2.xml')
    transactions = parser.parse_xml()
    parser.save_to_json()
    
    # Create dictionary for fast lookup
    transactions_dict = {txn['id']: txn for txn in transactions}
    
    print(f"Loaded {len(transactions)} transactions")
    
    # Create server with data
    server = HTTPServer(('localhost', port), TransactionAPIHandler)
    
    # Attach data to server instance
    server.transactions = transactions
    server.transactions_dict = transactions_dict
    
    print(f'🚀 Server running on http://localhost:{port}')
    print('📝 Available endpoints:')
    print('   GET    /transactions')
    print('   GET    /transactions/{id}')
    print('   POST   /transactions')
    print('   PUT    /transactions/{id}')
    print('   DELETE /transactions/{id}')
    print('')
    print('🔐 Authentication:')
    print('   Username: admin, Password: password123')
    print('   Username: user,  Password: user123')
    print('')
    print('Press Ctrl+C to stop the server')
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        server.server_close()

if __name__ == '__main__':
    run_server()