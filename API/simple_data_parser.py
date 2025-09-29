import xml.etree.ElementTree as ET
import json
from datetime import datetime

class SimpleDataParser:
    """Simple XML to JSON parser for SMS data - Beginner friendly version"""
    
    def __init__(self, xml_file_path):
        # Store the file path we want to read
        self.xml_file_path = xml_file_path
        # Create empty list to store all transactions
        self.transactions = []
    
    def parse_xml(self):
        """Read XML file and convert each SMS to a dictionary"""
        try:
            # Load and parse the XML file
            tree = ET.parse(self.xml_file_path)
            root = tree.getroot()
            
            # Go through each SMS message in the XML
            for sms in root.findall('sms'):
                # Create a dictionary for this transaction
                transaction = {}
                
                # Get basic information from XML attributes
                transaction['id'] = int(sms.get('id', 0))
                transaction['address'] = sms.get('address', '')
                transaction['body'] = sms.get('body', '')
                transaction['read_state'] = sms.get('read_state', '0')
                transaction['date'] = sms.get('date', '')
                transaction['type'] = sms.get('type', '')
                
                # Extract more useful information from the SMS body
                sms_body = sms.get('body', '')
                transaction['transaction_type'] = self.find_transaction_type(sms_body)
                transaction['amount'] = self.find_amount(sms_body)
                transaction['sender'] = self.find_sender(sms_body)
                transaction['receiver'] = self.find_receiver(sms_body)
                transaction['timestamp'] = self.fix_timestamp(sms.get('date', ''))
                
                # Add this transaction to our list
                self.transactions.append(transaction)
            
            return self.transactions
        
        except Exception as error:
            print(f"Error reading XML file: {error}")
            return []
    
    def find_transaction_type(self, sms_body):
        """Look at SMS text to figure out what type of transaction it is"""
        # Make text lowercase to make comparison easier
        text = sms_body.lower()
        
        # Check for different keywords
        if 'sent' in text:
            return 'sent'
        elif 'received' in text:
            return 'received'
        elif 'withdraw' in text:
            return 'withdrawal'
        elif 'deposit' in text:
            return 'deposit'
        else:
            return 'unknown'
    
    def find_amount(self, sms_body):
        """Find the money amount in the SMS text"""
        import re
        # Look for numbers that might be money amounts
        number_matches = re.findall(r'[\d,]+\.?\d*', sms_body)
        
        if number_matches:
            # Take the first number and remove commas
            amount_text = number_matches[0].replace(',', '')
            try:
                return float(amount_text)
            except:
                return 0.0
        else:
            return 0.0
    
    def find_sender(self, sms_body):
        """Try to find who sent the money"""
        text = sms_body.lower()
        if 'from' in text:
            # Split the text at 'from' and get the next word
            parts = text.split('from')
            if len(parts) > 1:
                words = parts[1].split()
                if words:
                    return words[0]
        return "Unknown"
    
    def find_receiver(self, sms_body):
        """Try to find who received the money"""
        text = sms_body.lower()
        if 'to' in text:
            # Split the text at 'to' and get the next word
            parts = text.split('to')
            if len(parts) > 1:
                words = parts[1].split()
                if words:
                    return words[0]
        return "Unknown"
    
    def fix_timestamp(self, timestamp_text):
        """Convert timestamp number to readable date"""
        try:
            # Convert from milliseconds to seconds and then to date
            timestamp_number = int(timestamp_text)
            readable_date = datetime.fromtimestamp(timestamp_number/1000).isoformat()
            return readable_date
        except:
            # If conversion fails, just return original text
            return timestamp_text
    
    def save_to_json(self, output_file='simple_transactions.json'):
        """Save all transactions to a JSON file"""
        # Open file and write JSON data
        with open(output_file, 'w') as file:
            json.dump(self.transactions, file, indent=2)
        print(f"Saved {len(self.transactions)} transactions to {output_file}")

# Test the parser if this file is run directly
if __name__ == '__main__':
    # Create parser and parse XML
    parser = SimpleDataParser('modified_sms_v2.xml')
    transactions = parser.parse_xml()
    
    print(f"Found {len(transactions)} transactions")
    
    # Save to JSON file
    parser.save_to_json()
    
    # Show first transaction as example
    if transactions:
        print("Example transaction:")
        print(transactions[0])