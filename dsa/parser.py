import json
import os
import re
import xml.etree.ElementTree as ET
from datetime import datetime


DATA_FILE_NAME = "modified_sms_v2.xml"
# Point to the API directory where the XML currently lives
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "API")
DATA_FILE_PATH = os.path.join(DATA_DIR, DATA_FILE_NAME)


def _parse_amount(body_text):
    """Extract amount from SMS body text"""
    if not body_text:
        return 0.0
    
    # Look for patterns like "2000 RWF", "1,000 RWF", "10,900 RWF"
    amount_patterns = [
        r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*RWF',  # Standard RWF format
        r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*RWF',      # Any RWF format
        r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',        # Just numbers with commas
    ]
    
    for pattern in amount_patterns:
        matches = re.findall(pattern, body_text)
        if matches:
            # Take the first (usually largest) amount found
            amount_str = matches[0].replace(',', '')
            try:
                return float(amount_str)
            except ValueError:
                continue
    
    return 0.0


def _extract_transaction_type(body_text):
    """Determine transaction type from SMS body"""
    if not body_text:
        return "unknown"
    
    body_lower = body_text.lower()
    
    if 'received' in body_lower or 'has been added' in body_lower:
        return 'received'
    elif 'deposit' in body_lower:
        return 'deposit'  
    elif 'transferred' in body_lower:
        return 'transfer'
    elif 'payment' in body_lower and 'completed' in body_lower:
        return 'payment'
    elif 'airtime' in body_lower:
        return 'airtime'
    elif 'withdraw' in body_lower:
        return 'withdrawal'
    else:
        return 'unknown'


def _extract_sender_receiver(body_text, transaction_type):
    """Extract sender and receiver information from SMS body"""
    if not body_text:
        return "Unknown", "Unknown"
    
    sender = "Unknown"
    receiver = "Unknown"
    
    # For received money
    if transaction_type == 'received':
        # Pattern: "You have received X RWF from Name (*********013)"
        match = re.search(r'from\s+([^(]+)', body_text, re.IGNORECASE)
        if match:
            sender = match.group(1).strip()
            receiver = "You"
    
    # For transfers
    elif transaction_type == 'transfer':
        # Pattern: "X RWF transferred to Name (phone) from account"
        match = re.search(r'transferred to\s+([^(]+)', body_text, re.IGNORECASE)
        if match:
            receiver = match.group(1).strip()
            sender = "You"
    
    # For payments
    elif transaction_type == 'payment':
        # Pattern: "Your payment of X RWF to Name"
        match = re.search(r'payment.*?to\s+([^0-9]+)', body_text, re.IGNORECASE)
        if match:
            receiver = match.group(1).strip()
            sender = "You"
    
    # For deposits
    elif transaction_type == 'deposit':
        sender = "Bank/Agent"
        receiver = "You"
    
    # For airtime
    elif transaction_type == 'airtime':
        sender = "You"
        receiver = "Airtime Service"
    
    return sender, receiver


def _convert_timestamp(date_str):
    """Convert timestamp from milliseconds to ISO format"""
    if not date_str:
        return datetime.now().isoformat()
    
    try:
        # Convert from milliseconds to seconds
        timestamp = int(date_str) / 1000
        return datetime.fromtimestamp(timestamp).isoformat()
    except (ValueError, TypeError):
        return datetime.now().isoformat()


def _extract_transaction_id(body_text):
    """Extract transaction ID from SMS body"""
    if not body_text:
        return None
    
    # Look for patterns like "TxId: 73214484437" or "Financial Transaction Id: 76662021700"
    patterns = [
        r'TxId:\s*(\d+)',
        r'Financial Transaction Id:\s*(\d+)',
        r'Transaction Id:\s*(\d+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, body_text, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None


def parse_sms_xml(file_path=DATA_FILE_PATH):
    """Parse SMS XML file and extract transaction data formatted for database schema"""
    if not os.path.exists(file_path):
        raise FileNotFoundError("Data file not found: %s" % file_path)

    tree = ET.parse(file_path)
    root = tree.getroot()

    transactions = []
    transaction_id = 1

    for sms in root.findall(".//sms"):
        body = sms.get('body', '')
        
        # Skip non-financial SMS
        if not body or 'RWF' not in body:
            continue
        
        # Extract transaction details
        transaction_type = _extract_transaction_type(body)
        amount = _parse_amount(body)
        sender, receiver = _extract_sender_receiver(body, transaction_type)
        timestamp = _convert_timestamp(sms.get('date', ''))
        tx_id = _extract_transaction_id(body) or str(transaction_id)
        
        # Skip if no meaningful amount found
        if amount <= 0:
            continue
        
        # Create transaction record matching database schema
        record = {
            "txn_id": transaction_id,
            "transaction_id": tx_id,  # Original SMS transaction ID
            "sender": sender,
            "receiver": receiver,
            "amount": amount,
            "txn_date": timestamp,
            "transaction_type": transaction_type,
            "status": "completed",  # Most SMS notifications are for completed transactions
            "raw_message": body,
            "created_at": datetime.now().isoformat()
        }
        
        transactions.append(record)
        transaction_id += 1

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
