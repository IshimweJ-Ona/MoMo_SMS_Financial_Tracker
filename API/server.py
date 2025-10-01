import base64
import json
import os
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer

# Inline XML parser and in-memory datastore so server.py is self-contained

class SMSDataParser:
    def __init__(self, xml_file_path):
        self.xml_file_path = xml_file_path
        self.transactions = []

    def parse_xml(self):
        try:
            tree = ET.parse(self.xml_file_path)
            root = tree.getroot()
            for sms in root.findall('sms'):
                body = sms.get('body', '')
                tx = {
                    "id": self._safe_int(sms.get('id', '0')),
                    "address": sms.get('address', ''),
                    "body": body,
                    "read_state": sms.get('read_state', '0'),
                    "date": sms.get('date', ''),
                    "type": sms.get('type', ''),
                    "transaction_type": self._extract_transaction_type(body),
                    "amount": self._extract_amount(body),
                    "sender": self._extract_sender(body),
                    "receiver": self._extract_receiver(body),
                    "timestamp": self._convert_timestamp(sms.get('date', '')),
                }
                self.transactions.append(tx)
            return self.transactions
        except Exception:
            return []

    def _extract_transaction_type(self, body):
        lower_body = (body or '').lower()
        if 'received' in lower_body:
            return 'received'
        if 'withdraw' in lower_body:
            return 'withdrawal'
        if 'deposit' in lower_body:
            return 'deposit'
        if 'transferred' in lower_body or 'payment' in lower_body or 'sent' in lower_body:
            return 'sent'
        return 'unknown'

    def _extract_amount(self, body):
        import re as _re
        if not body:
            return 0.0
        nums = _re.findall(r"[\d,]+\.?\d*", body)
        return float(nums[0].replace(',', '')) if nums else 0.0

    def _extract_sender(self, body):
        lower_body = (body or '').lower()
        if 'from' in lower_body:
            parts = lower_body.split('from', 1)[1].strip().split()
            return parts[0] if parts else 'Unknown'
        if 'you ' in lower_body:
            return 'You'
        return 'Unknown'

    def _extract_receiver(self, body):
        lower_body = (body or '').lower()
        if ' to ' in lower_body:
            parts = lower_body.split(' to ', 1)[1].strip().split()
            return parts[0] if parts else 'Unknown'
        return 'Unknown'

    def _convert_timestamp(self, ts):
        try:
            return datetime.fromtimestamp(int(ts) / 1000).isoformat()
        except Exception:
            return ts or ''

    def _safe_int(self, v):
        try:
            return int(v)
        except Exception:
            return 0


class InMemoryStore:
    def __init__(self):
        self.transactions = []
        self.id_to_transaction = {}
        self._next_id = 1

    def load_from_xml(self, file_path=None):
        xml_path = file_path or os.path.join(os.path.dirname(__file__), "modified_sms_v2.xml")
        parser = SMSDataParser(xml_path)
        records = parser.parse_xml()
        self.transactions = []
        self.id_to_transaction = {}
        self._next_id = 1
        for record in records:
            tx_id = str(record.get("id") or '').strip()
            if not tx_id or tx_id == '0':
                tx_id = str(self._generate_id())
            else:
                try:
                    self._next_id = max(self._next_id, int(tx_id) + 1)
                except Exception:
                    tx_id = str(self._generate_id())
            tx = {
                "id": tx_id,
                "transaction_type": record.get("transaction_type", ""),
                "amount": float(record.get("amount", 0.0)),
                "sender": record.get("sender", ""),
                "receiver": record.get("receiver", ""),
                "timestamp": record.get("timestamp", ""),
            }
            self.transactions.append(tx)
            self.id_to_transaction[tx_id] = tx

    def _generate_id(self):
        new_id = str(self._next_id)
        self._next_id += 1
        return new_id

    # CRUD operations
    def list_transactions(self):
        return list(self.transactions)

    def get_transaction(self, tx_id):
        return self.id_to_transaction.get(str(tx_id))

    def create_transaction(self, data):
        new_id = self._generate_id()
        tx = {
            "id": new_id,
            "transaction_type": data.get("transaction_type", ""),
            "amount": float(data.get("amount", 0.0)),
            "sender": data.get("sender", ""),
            "receiver": data.get("receiver", ""),
            "timestamp": data.get("timestamp", datetime.now().isoformat()),
        }
        self.transactions.append(tx)
        self.id_to_transaction[new_id] = tx
        return tx

    def update_transaction(self, tx_id, data):
        tx = self.id_to_transaction.get(str(tx_id))
        if not tx:
            return None
        if "transaction_type" in data:
            tx["transaction_type"] = data["transaction_type"]
        if "amount" in data:
            tx["amount"] = float(data["amount"])
        if "sender" in data:
            tx["sender"] = data["sender"]
        if "receiver" in data:
            tx["receiver"] = data["receiver"]
        if "timestamp" in data:
            tx["timestamp"] = data["timestamp"]
        return tx

    def delete_transaction(self, tx_id):
        tx = self.id_to_transaction.pop(str(tx_id), None)
        if not tx:
            return False
        self.transactions = [t for t in self.transactions if t["id"] != str(tx_id)]
        return True


def load_default_store():
    store = InMemoryStore()
    store.load_from_xml()
    return store

USERNAME = "admin"
PASSWORD = "password123"


def parse_basic_auth(header):
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
    store = load_default_store()

    def _send_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _unauthorized(self):
        self.send_response(HTTPStatus.UNAUTHORIZED)
        self.send_header("WWW-Authenticate", "Basic realm=\"Transactions API\"")
        self.end_headers()

    def _authorize(self):
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
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b""
        if not raw:
            return {}
        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            return {}

    def do_GET(self):
        if not self._authorize():
            return
        if self.path == "/transactions":
            data = self.store.list_transactions()
            self._send_json(HTTPStatus.OK, data)
            return
        match = re.fullmatch(r"/transactions/([^/]+)", self.path)
        if match:
            tx_id = match.group(1)
            tx = self.store.get_transaction(tx_id)
            if not tx:
                self._send_json(HTTPStatus.NOT_FOUND, {"error": "Not Found"})
            else:
                self._send_json(HTTPStatus.OK, tx)
            return
        self._send_json(HTTPStatus.NOT_FOUND, {"error": "Not Found"})

    def do_POST(self):
        if not self._authorize():
            return
        if self.path == "/transactions":
            payload = self._read_json()
            tx = self.store.create_transaction(payload)
            self._send_json(HTTPStatus.CREATED, tx)
            return
        self._send_json(HTTPStatus.NOT_FOUND, {"error": "Not Found"})

    def do_PUT(self):
        if not self._authorize():
            return
        match = re.fullmatch(r"/transactions/([^/]+)", self.path)
        if match:
            tx_id = match.group(1)
            payload = self._read_json()
            tx = self.store.update_transaction(tx_id, payload)
            if not tx:
                self._send_json(HTTPStatus.NOT_FOUND, {"error": "Not Found"})
            else:
                self._send_json(HTTPStatus.OK, tx)
            return
        self._send_json(HTTPStatus.NOT_FOUND, {"error": "Not Found"})

    def do_DELETE(self):
        if not self._authorize():
            return
        match = re.fullmatch(r"/transactions/([^/]+)", self.path)
        if match:
            tx_id = match.group(1)
            ok = self.store.delete_transaction(tx_id)
            if not ok:
                self._send_json(HTTPStatus.NOT_FOUND, {"error": "Not Found"})
            else:
                self._send_json(HTTPStatus.NO_CONTENT, {})
            return
        self._send_json(HTTPStatus.NOT_FOUND, {"error": "Not Found"})

    def log_message(self, format, *args):
        return


def run(host="127.0.0.1", port=8000):
    server = HTTPServer((host, port), RequestHandler)
    print("Server running on http://%s:%d" % (host, port))
    server.serve_forever()


if __name__ == "__main__":
    run()
