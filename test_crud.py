#!/usr/bin/env python3
"""
Direct test of CRUD operations without HTTP server
"""

import sys
import os
sys.path.append('API')
from datastore import InMemoryStore

def test_crud_operations():
    """Test all CRUD operations directly on the datastore"""
    print("Testing CRUD Operations")
    print("=" * 40)
    
    # Initialize store
    store = InMemoryStore()
    store.load_from_xml()
    
    print(f"Loaded {len(store.transactions)} transactions from XML")
    
    # Test READ - list all
    print("\n1. Testing LIST transactions...")
    all_transactions = store.list_transactions()
    print(f" Found {len(all_transactions)} transactions")
    
    if all_transactions:
        # Test READ - get single
        print(f"\n2. Testing GET single transaction...")
        first_tx = all_transactions[0]
        retrieved = store.get_transaction(first_tx['id'])
        if retrieved and retrieved['id'] == first_tx['id']:
            print(f" Successfully retrieved transaction {first_tx['id']}")
        else:
            print(" Failed to retrieve transaction")
    
    # Test CREATE
    print(f"\n3. Testing CREATE transaction...")
    new_data = {
        "transaction_type": "test",
        "amount": 123.45,
        "sender": "test_sender", 
        "receiver": "test_receiver",
        "timestamp": "2024-09-29T16:00:00Z"
    }
    
    created = store.create_transaction(new_data)
    if created and 'id' in created:
        print(f" Successfully created transaction with ID {created['id']}")
        
        # Test UPDATE
        print(f"\n4. Testing UPDATE transaction...")
        update_data = {"amount": 999.99, "sender": "updated_sender"}
        updated = store.update_transaction(created['id'], update_data)
        
        if updated and updated['amount'] == 999.99:
            print(f" Successfully updated transaction {created['id']}")
            
            # Test DELETE
            print(f"\n5. Testing DELETE transaction...")
            deleted = store.delete_transaction(created['id'])
            if deleted:
                print(f" Successfully deleted transaction {created['id']}")
                
                # Verify deletion
                check = store.get_transaction(created['id'])
                if not check:
                    print(" Transaction properly removed")
                else:
                    print(" Transaction still exists after deletion")
            else:
                print(" Failed to delete transaction")
        else:
            print(" Failed to update transaction")
    else:
        print(" Failed to create transaction")
    
    print("\n" + "=" * 40)
    print("CRUD testing complete!")

def test_authentication_logic():
    """Test authentication functions"""
    print("\nTesting Authentication Logic")
    print("=" * 30)
    
    # Import server functions
    import sys
    sys.path.append('API')
    from server import parse_basic_auth
    import base64
    
    # Test valid auth
    valid_creds = base64.b64encode(b"admin:password123").decode()
    result = parse_basic_auth(f"Basic {valid_creds}")
    if result == ("admin", "password123"):
        print(" Valid credentials parsed correctly")
    else:
        print(" Failed to parse valid credentials")
    
    # Test invalid auth
    result = parse_basic_auth("Invalid header")
    if result is None:
        print(" Invalid credentials rejected")
    else:
        print(" Invalid credentials not rejected")

if __name__ == "__main__":
    test_crud_operations()
    test_authentication_logic()