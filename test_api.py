#!/usr/bin/env python3
"""
Test script for SMS Financial Tracker API
Tests all CRUD operations with authentication
"""

import json
import base64
import urllib.request
import urllib.parse
import time
import sys

BASE_URL = "http://127.0.0.1:8000"
USERNAME = "admin"
PASSWORD = "password123"

def make_request(method, path, data=None, auth=True):
    """Make HTTP request with optional authentication"""
    url = BASE_URL + path
    headers = {}
    
    if auth:
        credentials = base64.b64encode(f"{USERNAME}:{PASSWORD}".encode()).decode()
        headers["Authorization"] = f"Basic {credentials}"
    
    if data:
        headers["Content-Type"] = "application/json"
        data = json.dumps(data).encode()
    
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as response:
            return response.getcode(), response.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode() if e.fp else str(e)

def test_authentication():
    """Test authentication"""
    print("Testing authentication...")
    
    # Test with valid credentials
    status, data = make_request("GET", "/transactions", auth=True)
    if status == 200:
        print("✅ Valid credentials accepted")
    else:
        print(f"❌ Valid credentials failed: {status}")
    
    # Test without credentials
    status, data = make_request("GET", "/transactions", auth=False)
    if status == 401:
        print("✅ Invalid credentials rejected")
    else:
        print(f"❌ Invalid credentials not rejected: {status}")

def test_get_transactions():
    """Test GET /transactions"""
    print("\nTesting GET /transactions...")
    status, data = make_request("GET", "/transactions")
    
    if status == 200:
        transactions = json.loads(data)
        print(f"✅ GET /transactions successful - {len(transactions)} transactions found")
        return transactions
    else:
        print(f"❌ GET /transactions failed: {status}")
        return []

def test_get_single_transaction(tx_id):
    """Test GET /transactions/{id}"""
    print(f"\nTesting GET /transactions/{tx_id}...")
    status, data = make_request("GET", f"/transactions/{tx_id}")
    
    if status == 200:
        transaction = json.loads(data)
        print(f"✅ GET /transactions/{tx_id} successful")
        return transaction
    else:
        print(f"❌ GET /transactions/{tx_id} failed: {status}")
        return None

def test_create_transaction():
    """Test POST /transactions"""
    print("\nTesting POST /transactions...")
    new_transaction = {
        "transaction_type": "test",
        "amount": 123.45,
        "sender": "test_sender",
        "receiver": "test_receiver",
        "timestamp": "2024-09-29T16:00:00Z"
    }
    
    status, data = make_request("POST", "/transactions", new_transaction)
    
    if status == 201:
        transaction = json.loads(data)
        print(f"✅ POST /transactions successful - created ID {transaction['id']}")
        return transaction
    else:
        print(f"❌ POST /transactions failed: {status}")
        return None

def test_update_transaction(tx_id):
    """Test PUT /transactions/{id}"""
    print(f"\nTesting PUT /transactions/{tx_id}...")
    update_data = {"amount": 999.99, "sender": "updated_sender"}
    
    status, data = make_request("PUT", f"/transactions/{tx_id}", update_data)
    
    if status == 200:
        transaction = json.loads(data)
        print(f"✅ PUT /transactions/{tx_id} successful")
        return transaction
    else:
        print(f"❌ PUT /transactions/{tx_id} failed: {status}")
        return None

def test_delete_transaction(tx_id):
    """Test DELETE /transactions/{id}"""
    print(f"\nTesting DELETE /transactions/{tx_id}...")
    status, data = make_request("DELETE", f"/transactions/{tx_id}")
    
    if status == 204:
        print(f"✅ DELETE /transactions/{tx_id} successful")
        return True
    else:
        print(f"❌ DELETE /transactions/{tx_id} failed: {status}")
        return False

def main():
    print("SMS Financial Tracker API Test")
    print("=" * 40)
    
    # Test authentication
    test_authentication()
    
    # Test GET all transactions
    transactions = test_get_transactions()
    
    if transactions:
        # Test GET single transaction
        first_tx = transactions[0]
        test_get_single_transaction(first_tx["id"])
    
    # Test CREATE
    new_tx = test_create_transaction()
    
    if new_tx:
        # Test UPDATE
        updated_tx = test_update_transaction(new_tx["id"])
        
        # Test DELETE
        test_delete_transaction(new_tx["id"])
    
    print("\n" + "=" * 40)
    print("API testing complete!")

if __name__ == "__main__":
    main()