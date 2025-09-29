import json
import os
import re
import xml.etree.ElementTree as ET
from datetime import datetime


DATA_FILE_NAME = "modified_sms_v2_clean.xml"
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
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
    """Extract amount from text using regex"""
    if not value:
        return 0.0
    # Look for patterns like "2000 RWF", "1,000 RWF", etc.
    amount_match = re.search(r'([0-9,]+)\s*RWF', str(value))
    if amount_match:
        cleaned = amount_match.group(1).replace(",", "")
        try:
            return float(cleaned)
        except ValueError:
            return 0.0
    return 0.0


def _parse_transaction_type(body):
    """Determine transaction type from SMS body"""
    if not body:
        return "unknown"
    
    body_lower = body.lower()
    if "received" in body_lower and "from" in body_lower:
        return "receive"
    elif "payment of" in body_lower or "transferred to" in body_lower:
        return "send"
    elif "bank deposit" in body_lower or "deposit of" in body_lower:
        return "deposit"
    elif "airtime" in body_lower:
        return "airtime"
    else:
        return "other"


def _parse_sender_receiver(body, transaction_type):
    """Extract sender and receiver from SMS body"""
    sender = ""
    receiver = ""
    
    if transaction_type == "receive":
        # Pattern: "received X RWF from NAME"
        match = re.search(r'from\s+([^(]+)\s*\(', body)
        if match:
            sender = match.group(1).strip()
            receiver = "me"
    elif transaction_type == "send":
        # Pattern: "payment of X RWF to NAME" or "transferred to NAME"
        match = re.search(r'(?:payment of [^to]+to|transferred to)\s+([^(]+)\s*(?:\(|\s|$)', body)
        if match:
            sender = "me"
            receiver = match.group(1).strip()
    elif transaction_type == "deposit":
        sender = "bank"
        receiver = "me"
    
    return sender, receiver


def _parse_timestamp(date_str, readable_date_str):
    """Convert timestamp to ISO format"""
    try:
        # Try to parse readable date first
        if readable_date_str:
            # Format: "10 May 2024 4:30:58 PM"
            dt = datetime.strptime(readable_date_str, "%d %b %Y %I:%M:%S %p")
            return dt.isoformat() + "Z"
    except:
        pass
    
    try:
        # Fallback to timestamp in milliseconds
        if date_str:
            timestamp_ms = int(date_str)
            dt = datetime.fromtimestamp(timestamp_ms / 1000)
            return dt.isoformat() + "Z"
    except:
        pass
    
    return ""


def _parse_sms_line(line):
    """Parse a single SMS line using regex"""
    # Extract SMS attributes using regex
    sms_pattern = r'<sms[^>]*body="([^"]*?)"[^>]*date="([^"]*?)"[^>]*readable_date="([^"]*?)"[^>]*/>'
    match = re.search(sms_pattern, line)
    
    if match:
        return {
            'body': match.group(1),
            'date': match.group(2),
            'readable_date': match.group(3)
        }
    return None


def parse_sms_xml(file_path=DATA_FILE_PATH):
    if not os.path.exists(file_path):
        raise FileNotFoundError("Data file not found: %s" % file_path)

    transactions = []
    
    try:
        # First try XML parsing
        tree = ET.parse(file_path)
        root = tree.getroot()
        sms_elements = root.findall(".//sms")
        
        for i, sms in enumerate(sms_elements[:100]):  # Limit to first 100 for testing
            body = sms.get("body", "")
            date_str = sms.get("date", "")
            readable_date = sms.get("readable_date", "")
            
            # Skip if no body or no financial content
            if not body or "RWF" not in body:
                continue
                
            transaction_type = _parse_transaction_type(body)
            amount = _parse_amount(body)
            sender, receiver = _parse_sender_receiver(body, transaction_type)
            timestamp = _parse_timestamp(date_str, readable_date)
            
            record = {
                "id": str(i + 1),  # Use index as ID since SMS doesn't have transaction IDs
                "transaction_type": transaction_type,
                "amount": amount,
                "sender": sender,
                "receiver": receiver,
                "timestamp": timestamp,
                "original_body": body[:100] + "..." if len(body) > 100 else body  # Keep for reference
            }
            
            # Only add if we have meaningful data
            if amount > 0 and transaction_type != "unknown":
                transactions.append(record)
                
    except ET.ParseError:
        # Fallback to regex parsing if XML is malformed
        print("XML parsing failed, using regex fallback...")
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Find all SMS entries using regex
        sms_pattern = r'<sms[^>]+body="([^"]+)".*?date="([^"]+)".*?readable_date="([^"]+)"'
        matches = re.findall(sms_pattern, content, re.DOTALL)
        
        for i, (body, date_str, readable_date) in enumerate(matches[:100]):
            # Skip if no body or no financial content
            if not body or "RWF" not in body:
                continue
                
            transaction_type = _parse_transaction_type(body)
            amount = _parse_amount(body)
            sender, receiver = _parse_sender_receiver(body, transaction_type)
            timestamp = _parse_timestamp(date_str, readable_date)
            
            record = {
                "id": str(i + 1),
                "transaction_type": transaction_type,
                "amount": amount,
                "sender": sender,
                "receiver": receiver,
                "timestamp": timestamp,
                "original_body": body[:100] + "..." if len(body) > 100 else body
            }
            
            # Only add if we have meaningful data
            if amount > 0 and transaction_type != "unknown":
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
