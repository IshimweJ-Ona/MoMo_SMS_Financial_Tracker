from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import base64
from datetime import datetime

# Simple user database - in real apps this would be in a database
USERS = {
    "admin": "password123",
    "user": "user123"
}

# Import our simple data parser
from simple_data_parser import SimpleDataParser

class SimpleAPIHandler(BaseHTTPRequestHandler):
    """Simple HTTP request handler for transaction API - Beginner friendly"""
    
    def send_response_with_json(self, status_code, data):
        """Helper function to send JSON response"""
        # Set HTTP response code
        self.send_response(status_code)
        # Set headers to tell browser this is JSON
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
        # Send the actual data
        json_data = json.dumps(data)
        self.wfile.write(json_data.encode())
    
    def check_password(self):
        """Check if user provided correct username and password"""
        # Get the Authorization header
        auth_header = self.headers.get('Authorization')
        
        # Check if header exists and starts with 'Basic '
        if not auth_header or not auth_header.startswith('Basic '):
            return False
        
        # Decode the credentials
        try:
            # Remove 'Basic ' and decode from base64
            encoded_credentials = auth_header[6:]
            decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
            username, password = decoded_credentials.split(':', 1)
            
            # Check if username and password are correct
            return USERS.get(username) == password
        except:
            return False
    
    def get_transaction_id_from_url(self):
        """Extract transaction ID from URL path"""
        # Split URL path into parts: /transactions/123 -> ['', 'transactions', '123']
        path_parts = self.path.split('/')
        if len(path_parts) >= 3 and path_parts[1] == 'transactions':
            try:
                # Try to convert the third part to integer
                return int(path_parts[2])
            except:
                return None
        return None
    
    def read_request_body(self):
        """Read and parse JSON data from request body"""
        try:
            # Get how many bytes to read
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                # Read the data
                body = self.rfile.read(content_length)
                # Convert to Python dictionary
                return json.loads(body.decode('utf-8'))
            return {}
        except:
            return {}
    
    def do_OPTIONS(self):
        """Handle OPTIONS request for CORS"""
        self.send_response_with_json(200, {})
    
    def do_GET(self):
        """Handle GET requests - retrieve transactions"""
        # Check authentication first
        if not self.check_password():
            self.send_response_with_json(401, {'error': 'Please provide correct username and password'})
            return
        
        # Check if they want a specific transaction
        transaction_id = self.get_transaction_id_from_url()
        
        if transaction_id is not None:
            # Get single transaction: GET /transactions/123
            transaction = self.server.transactions_dict.get(transaction_id)
            if transaction:
                self.send_response_with_json(200, transaction)
            else:
                self.send_response_with_json(404, {'error': 'Transaction not found'})
        else:
            # Get all transactions: GET /transactions
            self.send_response_with_json(200, self.server.transactions)
    
    def do_POST(self):
        """Handle POST requests - create new transaction"""
        # Check authentication
        if not self.check_password():
            self.send_response_with_json(401, {'error': 'Please provide correct username and password'})
            return
        
        if self.path == '/transactions':
            try:
                # Read the new transaction data
                new_data = self.read_request_body()
                
                # Create a new ID
                existing_ids = [txn['id'] for txn in self.server.transactions]
                if existing_ids:
                    new_id = max(existing_ids) + 1
                else:
                    new_id = 1
                
                # Add the new ID to the transaction
                new_data['id'] = new_id
                
                # Add timestamp if not provided
                if 'timestamp' not in new_data:
                    new_data['timestamp'] = datetime.now().isoformat()
                
                # Add to our lists
                self.server.transactions.append(new_data)
                self.server.transactions_dict[new_id] = new_data
                
                # Send back the created transaction
                self.send_response_with_json(201, new_data)
            
            except Exception as error:
                self.send_response_with_json(400, {'error': f'Bad request: {str(error)}'})
    
    def do_PUT(self):
        """Handle PUT requests - update existing transaction"""
        # Check authentication
        if not self.check_password():
            self.send_response_with_json(401, {'error': 'Please provide correct username and password'})
            return
        
        transaction_id = self.get_transaction_id_from_url()
        if transaction_id is not None:
            # Find the transaction to update
            transaction = self.server.transactions_dict.get(transaction_id)
            if transaction:
                try:
                    # Read the update data
                    update_data = self.read_request_body()
                    
                    # Update the fields
                    for key, value in update_data.items():
                        if key != 'id':  # Don't allow changing the ID
                            transaction[key] = value
                    
                    # Update in the list too
                    for i, txn in enumerate(self.server.transactions):
                        if txn['id'] == transaction_id:
                            self.server.transactions[i] = transaction
                            break
                    
                    self.send_response_with_json(200, transaction)
                
                except Exception as error:
                    self.send_response_with_json(400, {'error': f'Bad request: {str(error)}'})
            else:
                self.send_response_with_json(404, {'error': 'Transaction not found'})
    
    def do_DELETE(self):
        """Handle DELETE requests - remove transaction"""
        # Check authentication
        if not self.check_password():
            self.send_response_with_json(401, {'error': 'Please provide correct username and password'})
            return
        
        transaction_id = self.get_transaction_id_from_url()
        if transaction_id is not None:
            # Check if transaction exists
            if transaction_id in self.server.transactions_dict:
                # Remove from dictionary
                del self.server.transactions_dict[transaction_id]
                
                # Remove from list
                self.server.transactions = [txn for txn in self.server.transactions if txn['id'] != transaction_id]
                
                self.send_response_with_json(200, {'message': 'Transaction deleted successfully'})
            else:
                self.send_response_with_json(404, {'error': 'Transaction not found'})

def start_simple_server(port=8000):
    """Start the simple HTTP server"""
    print("Loading SMS transaction data...")
    
    # Parse the XML data using our simple parser
    parser = SimpleDataParser('modified_sms_v2.xml')
    transactions = parser.parse_xml()
    parser.save_to_json('simple_transactions.json')
    
    # Create a dictionary for fast lookups
    transactions_dict = {}
    for transaction in transactions:
        transactions_dict[transaction['id']] = transaction
    
    print(f"Loaded {len(transactions)} transactions")
    
    # Create the server
    server = HTTPServer(('localhost', port), SimpleAPIHandler)
    
    # Give the server access to our data
    server.transactions = transactions
    server.transactions_dict = transactions_dict
    
    # Show information to user
    print(f'Simple API Server running on http://localhost:{port}')
    print('')
    print('You can use these URLs:')
    print('   GET    http://localhost:8000/transactions        (get all transactions)')
    print('   GET    http://localhost:8000/transactions/1      (get transaction with ID 1)')
    print('   POST   http://localhost:8000/transactions        (create new transaction)')
    print('   PUT    http://localhost:8000/transactions/1      (update transaction with ID 1)')
    print('   DELETE http://localhost:8000/transactions/1      (delete transaction with ID 1)')
    print('')
    print('Login credentials:')
    print('   Username: admin')
    print('   Password: password123')
    print('')
    print('Press Ctrl+C to stop the server')
    
    try:
        # Start serving requests
        server.serve_forever()
    except KeyboardInterrupt:
        print("\\nServer stopped")
        server.server_close()

# Start the server if this file is run directly
if __name__ == '__main__':
    start_simple_server()