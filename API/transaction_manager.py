#!/usr/bin/env python3
"""
Transaction Manager for MoMo SMS Financial Tracker
Handles transaction data in memory, eliminating need for large JSON files
"""

import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Any, Optional

# Add parent directory to path to import parser
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from dsa.parser import parse_sms_xml


class TransactionManager:
    """
    Manages transaction data in memory with CRUD operations
    Loads data from XML once, keeps in memory for fast access
    """
    
    def __init__(self, xml_file_path: str = None):
        self.xml_file_path = xml_file_path or os.path.join(os.path.dirname(__file__), "modified_sms_v2.xml")
        self.transactions: List[Dict[str, Any]] = []
        self.transactions_by_id: Dict[str, Dict[str, Any]] = {}
        self._next_id = 1
        self._load_transactions()
    
    def _load_transactions(self):
        """Load transactions from XML file into memory"""
        try:
            print(f"Loading transactions from {self.xml_file_path}...")
            self.transactions = parse_sms_xml(self.xml_file_path)
            
            # Create ID lookup dictionary and set next ID
            self.transactions_by_id = {}
            max_id = 0
            
            for transaction in self.transactions:
                tx_id = str(transaction.get('txn_id', transaction.get('id', 0)))
                self.transactions_by_id[tx_id] = transaction
                try:
                    max_id = max(max_id, int(tx_id))
                except (ValueError, TypeError):
                    pass
            
            self._next_id = max_id + 1
            print(f"Loaded {len(self.transactions)} transactions into memory")
            
        except Exception as e:
            print(f"Error loading transactions: {e}")
            self.transactions = []
            self.transactions_by_id = {}
    
    def get_all_transactions(self) -> List[Dict[str, Any]]:
        """Get all transactions"""
        return self.transactions.copy()
    
    def get_transaction_by_id(self, tx_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific transaction by ID"""
        return self.transactions_by_id.get(str(tx_id))
    
    def add_transaction(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new transaction"""
        # Generate new ID
        new_id = str(self._next_id)
        self._next_id += 1
        
        # Create transaction with required fields
        new_transaction = {
            "txn_id": int(new_id),
            "transaction_id": transaction_data.get("transaction_id", new_id),
            "sender": transaction_data.get("sender", "Unknown"),
            "receiver": transaction_data.get("receiver", "Unknown"),
            "amount": float(transaction_data.get("amount", 0.0)),
            "txn_date": transaction_data.get("txn_date", datetime.now().isoformat()),
            "transaction_type": transaction_data.get("transaction_type", "unknown"),
            "status": transaction_data.get("status", "pending"),
            "raw_message": transaction_data.get("raw_message", ""),
            "created_at": datetime.now().isoformat()
        }
        
        # Add to both storage structures
        self.transactions.append(new_transaction)
        self.transactions_by_id[new_id] = new_transaction
        
        return new_transaction
    
    def update_transaction(self, tx_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing transaction"""
        transaction = self.transactions_by_id.get(str(tx_id))
        if not transaction:
            return None
        
        # Update allowed fields
        updatable_fields = [
            "sender", "receiver", "amount", "transaction_type", 
            "status", "raw_message", "txn_date"
        ]
        
        for field in updatable_fields:
            if field in update_data:
                if field == "amount":
                    transaction[field] = float(update_data[field])
                else:
                    transaction[field] = update_data[field]
        
        # Update timestamp
        transaction["updated_at"] = datetime.now().isoformat()
        
        return transaction
    
    def delete_transaction(self, tx_id: str) -> bool:
        """Delete a transaction"""
        transaction = self.transactions_by_id.get(str(tx_id))
        if not transaction:
            return False
        
        # Remove from both storage structures
        self.transactions = [t for t in self.transactions if str(t.get('txn_id', t.get('id'))) != str(tx_id)]
        del self.transactions_by_id[str(tx_id)]
        
        return True
    
    def get_transactions_count(self) -> int:
        """Get total number of transactions"""
        return len(self.transactions)
    
    def search_transactions(self, **filters) -> List[Dict[str, Any]]:
        """Search transactions by various criteria"""
        results = self.transactions.copy()
        
        for field, value in filters.items():
            if field == "amount_min":
                results = [t for t in results if t.get("amount", 0) >= float(value)]
            elif field == "amount_max":
                results = [t for t in results if t.get("amount", 0) <= float(value)]
            elif field == "transaction_type":
                results = [t for t in results if t.get("transaction_type", "").lower() == str(value).lower()]
            elif field == "status":
                results = [t for t in results if t.get("status", "").lower() == str(value).lower()]
            elif field == "sender":
                results = [t for t in results if str(value).lower() in t.get("sender", "").lower()]
            elif field == "receiver":
                results = [t for t in results if str(value).lower() in t.get("receiver", "").lower()]
        
        return results
    
    def get_transaction_stats(self) -> Dict[str, Any]:
        """Get transaction statistics"""
        if not self.transactions:
            return {"total": 0, "total_amount": 0, "avg_amount": 0, "types": {}}
        
        total_amount = sum(t.get("amount", 0) for t in self.transactions)
        avg_amount = total_amount / len(self.transactions)
        
        # Count by type
        type_counts = {}
        for t in self.transactions:
            tx_type = t.get("transaction_type", "unknown")
            type_counts[tx_type] = type_counts.get(tx_type, 0) + 1
        
        return {
            "total": len(self.transactions),
            "total_amount": total_amount,
            "avg_amount": round(avg_amount, 2),
            "types": type_counts
        }
    
    def save_to_json(self, json_path: str) -> bool:
        """
        Optional: Save current transactions to JSON file
        (Only use this for backup/export purposes)
        """
        try:
            os.makedirs(os.path.dirname(json_path), exist_ok=True)
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(self.transactions, f, indent=2, ensure_ascii=False)
            print(f"Transactions exported to: {json_path}")
            return True
        except Exception as e:
            print(f"Error saving to JSON: {e}")
            return False
    
    def reload_from_xml(self) -> int:
        """Reload transactions from XML file (useful for development)"""
        old_count = len(self.transactions)
        self._load_transactions()
        new_count = len(self.transactions)
        print(f"Reloaded: {old_count} → {new_count} transactions")
        return new_count


# Global transaction manager instance
_transaction_manager = None

def get_transaction_manager() -> TransactionManager:
    """Get the global transaction manager instance"""
    global _transaction_manager
    if _transaction_manager is None:
        _transaction_manager = TransactionManager()
    return _transaction_manager


def save_transactions_json(transactions: List[Dict[str, Any]], json_path: str):
    """
    Utility function to save transactions to JSON file
    (As requested by user)
    """
    try:
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        with open(json_path, 'w', encoding='utf-8') as json_file:
            json.dump(transactions, json_file, indent=4, ensure_ascii=False)
        print(f"Transactions saved to JSON file: {json_path}")
    except Exception as e:
        print(f"Error saving JSON to {json_path}: {e}")


if __name__ == "__main__":
    """Test the transaction manager"""
    manager = TransactionManager()
    
    print(f"Loaded {manager.get_transactions_count()} transactions")
    print("\nTransaction Statistics:")
    stats = manager.get_transaction_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Test getting first transaction
    if manager.transactions:
        first_tx = manager.transactions[0]
        tx_id = str(first_tx.get('txn_id', first_tx.get('id')))
        print(f"\nFirst transaction (ID: {tx_id}):")
        print(f"  Sender: {first_tx.get('sender')}")
        print(f"  Receiver: {first_tx.get('receiver')}")
        print(f"  Amount: {first_tx.get('amount')} RWF")
        print(f"  Type: {first_tx.get('transaction_type')}")
