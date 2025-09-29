import base64
import json
import re
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer

from api.datastore import load_default_store

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
