import json
import os
import xml.etree.ElementTree as ET


DATA_FILE_NAME = "modified_sms_v2.xml"
# Point to the API directory where the XML currently lives
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "API")
DATA_FILE_PATH = os.path.join(DATA_DIR, DATA_FILE_NAME)


REQUIRED_FIELDS = [
    "id",
    "transaction_type",
    "amount",
    "sender",
    "receiver",
    "timestamp",
]


def _parse_amount(value):
    cleaned = str(value).replace(",", "").replace("$", "").strip()
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def parse_sms_xml(file_path=DATA_FILE_PATH):
    if not os.path.exists(file_path):
        raise FileNotFoundError("Data file not found: %s" % file_path)

    tree = ET.parse(file_path)
    root = tree.getroot()

    transactions = []

    for sms in root.findall(".//sms"):
        record = {}
        record["id"] = sms.get("id") or sms.findtext("id") or ""
        record["transaction_type"] = (
            sms.get("transaction_type")
            or sms.findtext("transaction_type")
            or sms.get("type")
            or sms.findtext("type")
            or ""
        )
        raw_amount = sms.get("amount") or sms.findtext("amount") or "0"
        record["amount"] = _parse_amount(raw_amount)
        record["sender"] = sms.get("sender") or sms.findtext("sender") or ""
        record["receiver"] = sms.get("receiver") or sms.findtext("receiver") or ""
        record["timestamp"] = sms.get("timestamp") or sms.findtext("timestamp") or ""

        if str(record["id"]).strip():
            transactions.append(record)

    return transactions


def save_as_json(output_path, records):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    parsed = parse_sms_xml()
    out = os.path.join(DATA_DIR, "parsed_sms.json")
    save_as_json(out, parsed)
    print("Parsed %d transactions -> %s" % (len(parsed), out))
