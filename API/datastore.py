import os
import json

# Use the robust parser that extracts fields from SMS body text
from api.data_parser import SMSDataParser


XML_FILE_PATH = os.path.join(os.path.dirname(__file__), "modified_sms_v2.xml")
PARSED_JSON = os.path.join(os.path.dirname(__file__), "transactions.json")


class InMemoryStore:
    def __init__(self):
        self.transactions = []
        self.id_to_transaction = {}
        self._next_id = 1

    def load_from_xml(self, file_path=None):
        xml_path = file_path or XML_FILE_PATH
        parser = SMSDataParser(xml_path)
        records = parser.parse_xml()
        self.transactions = []
        self.id_to_transaction = {}
        for record in records:
            tx_id = str(record.get("id") or "").strip()
            if not tx_id:
                tx_id = str(self._next_id)
                self._next_id += 1
            else:
                try:
                    self._next_id = max(self._next_id, int(tx_id) + 1)
                except ValueError:
                    pass

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
        # Cache to JSON for faster subsequent loads
        try:
            with open(PARSED_JSON, "w", encoding="utf-8") as f:
                json.dump(self.transactions, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _generate_id(self):
        new_id = str(self._next_id)
        self._next_id += 1
        return new_id

    # CRUD
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
            "timestamp": data.get("timestamp", ""),
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

    # DSA methods
    def linear_search_by_id(self, tx_id):
        target = str(tx_id)
        for tx in self.transactions:
            if tx.get("id") == target:
                return tx
        return None

    def dict_lookup_by_id(self, tx_id):
        return self.id_to_transaction.get(str(tx_id))

def load_default_store():
    store = InMemoryStore()
    if os.path.exists(PARSED_JSON):
        try:
            with open(PARSED_JSON, "r", encoding="utf-8") as f:
                records = json.load(f)
            store.transactions = []
            store.id_to_transaction = {}
            for rec in records:
                tx_id = str(rec.get("id", "")).strip() or store._generate_id()
                tx = {
                    "id": tx_id,
                    "transaction_type": rec.get("transaction_type", ""),
                    "amount": float(rec.get("amount", 0.0)),
                    "sender": rec.get("sender", ""),
                    "receiver": rec.get("receiver", ""),
                    "timestamp": rec.get("timestamp", ""),
                }
                store.transactions.append(tx)
                store.id_to_transaction[tx_id] = tx
        except Exception:
            store.load_from_xml()
    else:
        store.load_from_xml()
    return store
