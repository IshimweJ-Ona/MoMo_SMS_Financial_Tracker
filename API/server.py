import base64
import json
import re
from datetime import datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from transaction_manager import get_transaction_manager

# Authentication credentials
USERNAME = "admin"
PASSWORD = "password123"


def parse_basic_auth(header):
    """Parse Basic Authentication header"""
    if not header or not header.startswith("Basic "):
        return None
    try:
        encoded = header.split(" ", 1)[1]
        decoded = base64.b64decode(encoded).decode("utf-8")
        parts = decoded.split(":", 1)
        if len(parts) != 2:
            return None
        return parts[0], parts[1]
    except Exception:
        return None


class RequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for MoMo SMS Financial Tracker API"""
    
    # Use class variable to share transaction manager across all requests
    transaction_manager = None
    
    @classmethod
    def set_transaction_manager(cls, manager):
        cls.transaction_manager = manager

    def _send_json(self, status, payload):
        """Send JSON response"""
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")  # Enable CORS
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()
        self.wfile.write(body)

    def _unauthorized(self):
        """Send 401 Unauthorized response"""
        self.send_response(HTTPStatus.UNAUTHORIZED)
        self.send_header("WWW-Authenticate", "Basic realm=\"MoMo Transactions API\"")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

    def _authorize(self):
        """Check Basic Authentication"""
        header = self.headers.get("Authorization")
        creds = parse_basic_auth(header)
        if not creds:
            self._unauthorized()
            return False
        user, pwd = creds
        if user == USERNAME and pwd == PASSWORD:
            return True
        self._unauthorized()
        return False

    def _read_json(self):
        """Read and parse JSON from request body"""
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b""
        if not raw:
            return {}
        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            return {}

    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(HTTPStatus.OK)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self):
        """Handle GET requests"""
        if not self._authorize():
            return

        # GET /transactions - List all transactions
        if self.path == "/transactions":
            try:
                transactions = self.transaction_manager.get_all_transactions()
                # Convert to API format
                api_transactions = []
                for tx in transactions:
                    api_tx = {
                        "id": str(tx.get("txn_id", tx.get("id", ""))),
                        "transaction_id": tx.get("transaction_id", ""),
                        "transaction_type": tx.get("transaction_type", "unknown"),
                        "amount": float(tx.get("amount", 0.0)),
                        "sender": tx.get("sender", "Unknown"),
                        "receiver": tx.get("receiver", "Unknown"),
                        "timestamp": tx.get("txn_date", tx.get("timestamp", "")),
                        "status": tx.get("status", "completed"),
                        "raw_message": tx.get("raw_message", ""),
                        "created_at": tx.get("created_at", "")
                    }
                    api_transactions.append(api_tx)
                
                self._send_json(HTTPStatus.OK, api_transactions)
                return
            except Exception as e:
                self._send_json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": f"Failed to get transactions: {str(e)}"})
                return

        # GET /transactions/{id} - Get specific transaction
        match = re.fullmatch(r"/transactions/([^/]+)", self.path)
        if match:
            tx_id = match.group(1)
            try:
                transaction = self.transaction_manager.get_transaction_by_id(tx_id)
                if not transaction:
                    self._send_json(HTTPStatus.NOT_FOUND, {"error": "Transaction not found"})
                    return
                
                # Convert to API format
                api_tx = {
                    "id": str(transaction.get("txn_id", transaction.get("id", ""))),
                    "transaction_id": transaction.get("transaction_id", ""),
                    "transaction_type": transaction.get("transaction_type", "unknown"),
                    "amount": float(transaction.get("amount", 0.0)),
                    "sender": transaction.get("sender", "Unknown"),
                    "receiver": transaction.get("receiver", "Unknown"),
                    "timestamp": transaction.get("txn_date", transaction.get("timestamp", "")),
                    "status": transaction.get("status", "completed"),
                    "raw_message": transaction.get("raw_message", ""),
                    "created_at": transaction.get("created_at", ""),
                    "updated_at": transaction.get("updated_at", "")
                }
                
                self._send_json(HTTPStatus.OK, api_tx)
                return
            except Exception as e:
                self._send_json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": f"Failed to get transaction: {str(e)}"})
                return

        # GET /stats - Get transaction statistics (bonus endpoint)
        if self.path == "/stats":
            try:
                stats = self.transaction_manager.get_transaction_stats()
                self._send_json(HTTPStatus.OK, stats)
                return
            except Exception as e:
                self._send_json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": f"Failed to get stats: {str(e)}"})
                return

        # 404 for unknown paths
        self._send_json(HTTPStatus.NOT_FOUND, {"error": "Endpoint not found"})

    def do_POST(self):
        """Handle POST requests"""
        if not self._authorize():
            return

        # POST /transactions - Create new transaction
        if self.path == "/transactions":
            try:
                data = self._read_json()
                if not data:
                    self._send_json(HTTPStatus.BAD_REQUEST, {"error": "No data provided"})
                    return

                # Validate required fields
                required_fields = ["sender", "receiver", "amount"]
                missing_fields = [field for field in required_fields if not data.get(field)]
                if missing_fields:
                    self._send_json(HTTPStatus.BAD_REQUEST, {
                        "error": f"Missing required fields: {', '.join(missing_fields)}"
                    })
                    return

                # Create transaction
                new_transaction = self.transaction_manager.add_transaction(data)
                
                # Convert to API format
                api_tx = {
                    "id": str(new_transaction.get("txn_id")),
                    "transaction_id": new_transaction.get("transaction_id", ""),
                    "transaction_type": new_transaction.get("transaction_type", "unknown"),
                    "amount": float(new_transaction.get("amount", 0.0)),
                    "sender": new_transaction.get("sender", "Unknown"),
                    "receiver": new_transaction.get("receiver", "Unknown"),
                    "timestamp": new_transaction.get("txn_date", ""),
                    "status": new_transaction.get("status", "pending"),
                    "raw_message": new_transaction.get("raw_message", ""),
                    "created_at": new_transaction.get("created_at", "")
                }
                
                self._send_json(HTTPStatus.CREATED, api_tx)
                return
            except Exception as e:
                self._send_json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": f"Failed to create transaction: {str(e)}"})
                return

        # 404 for unknown paths
        self._send_json(HTTPStatus.NOT_FOUND, {"error": "Endpoint not found"})

    def do_PUT(self):
        """Handle PUT requests"""
        if not self._authorize():
            return

        # PUT /transactions/{id} - Update transaction
        match = re.fullmatch(r"/transactions/([^/]+)", self.path)
        if match:
            tx_id = match.group(1)
            try:
                data = self._read_json()
                if not data:
                    self._send_json(HTTPStatus.BAD_REQUEST, {"error": "No data provided"})
                    return

                updated_transaction = self.transaction_manager.update_transaction(tx_id, data)
                if not updated_transaction:
                    self._send_json(HTTPStatus.NOT_FOUND, {"error": "Transaction not found"})
                    return

                # Convert to API format
                api_tx = {
                    "id": str(updated_transaction.get("txn_id")),
                    "transaction_id": updated_transaction.get("transaction_id", ""),
                    "transaction_type": updated_transaction.get("transaction_type", "unknown"),
                    "amount": float(updated_transaction.get("amount", 0.0)),
                    "sender": updated_transaction.get("sender", "Unknown"),
                    "receiver": updated_transaction.get("receiver", "Unknown"),
                    "timestamp": updated_transaction.get("txn_date", ""),
                    "status": updated_transaction.get("status", "completed"),
                    "raw_message": updated_transaction.get("raw_message", ""),
                    "created_at": updated_transaction.get("created_at", ""),
                    "updated_at": updated_transaction.get("updated_at", "")
                }
                
                self._send_json(HTTPStatus.OK, api_tx)
                return
            except Exception as e:
                self._send_json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": f"Failed to update transaction: {str(e)}"})
                return

        # 404 for unknown paths
        self._send_json(HTTPStatus.NOT_FOUND, {"error": "Endpoint not found"})

    def do_DELETE(self):
        """Handle DELETE requests"""
        if not self._authorize():
            return

        # DELETE /transactions/{id} - Delete transaction
        match = re.fullmatch(r"/transactions/([^/]+)", self.path)
        if match:
            tx_id = match.group(1)
            try:
                success = self.transaction_manager.delete_transaction(tx_id)
                if not success:
                    self._send_json(HTTPStatus.NOT_FOUND, {"error": "Transaction not found"})
                    return

                self._send_json(HTTPStatus.OK, {"message": f"Transaction {tx_id} deleted successfully"})
                return
            except Exception as e:
                self._send_json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": f"Failed to delete transaction: {str(e)}"})
                return

        # 404 for unknown paths
        self._send_json(HTTPStatus.NOT_FOUND, {"error": "Endpoint not found"})

    def log_message(self, format, *args):
        """Suppress default logging"""
        return


def run(host="127.0.0.1", port=8000):
    """Start the HTTP server"""
    try:
        # Initialize transaction manager
        manager = get_transaction_manager()
        print(f"Loaded {manager.get_transactions_count()} transactions from XML")
        
        # Set the transaction manager for all request handlers
        RequestHandler.set_transaction_manager(manager)
        
        # Start server
        server = HTTPServer((host, port), RequestHandler)
        print(f"MoMo SMS Financial Tracker API running on http://{host}:{port}")
        print("Available endpoints:")
        print("  GET    /transactions     - List all transactions")
        print("  GET    /transactions/{id} - Get specific transaction")
        print("  POST   /transactions     - Create new transaction")
        print("  PUT    /transactions/{id} - Update transaction")
        print("  DELETE /transactions/{id} - Delete transaction")
        print("  GET    /stats           - Get transaction statistics")
        print(f"Authentication: {USERNAME} / {PASSWORD}")
        print("\nPress Ctrl+C to stop the server")
        
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")
    except Exception as e:
        print(f"Server error: {e}")


if __name__ == "__main__":
    run()