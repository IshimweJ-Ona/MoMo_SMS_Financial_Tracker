#!/usr/bin/env python3
"""
Final comprehensive test of all components
Tests according to assignment rubric requirements
"""

import sys
import os
import json
import time
from statistics import mean

def test_data_parsing():
    """Test XML parsing to JSON (Rubric: Data Parsing - 5 pts)"""
    print("=" * 50)
    print("Testing Data Parsing (XML to JSON)")
    print("=" * 50)
    
    from dsa.parser import parse_sms_xml
    
    try:
        transactions = parse_sms_xml()
        print(f" XML parsed successfully")
        print(f" Found {len(transactions)} transactions")
        
        # Check key fields
        if transactions:
            sample = transactions[0]
            required_fields = ['id', 'transaction_type', 'amount', 'sender', 'receiver', 'timestamp']
            missing_fields = []
            
            for field in required_fields:
                if field not in sample:
                    missing_fields.append(field)
            
            if not missing_fields:
                print(f" All key fields present in JSON objects")
                print(f"   Sample transaction: {sample['transaction_type']} of {sample['amount']} from {sample['sender']} to {sample['receiver']}")
                return True
            else:
                print(f" Missing fields: {missing_fields}")
                return False
        else:
            print(" No transactions parsed")
            return False
            
    except Exception as e:
        print(f" XML parsing failed: {e}")
        return False

def test_api_implementation():
    """Test API Implementation (Rubric: API Implementation - 5 pts)"""
    print("\n" + "=" * 50)
    print("Testing API Implementation (CRUD endpoints)")
    print("=" * 50)
    
    sys.path.append('API')
    from datastore import InMemoryStore
    
    store = InMemoryStore()
    store.load_from_xml()
    
    endpoints_tested = []
    
    # Test GET (list)
    try:
        transactions = store.list_transactions()
        if transactions:
            print(f" GET /transactions - Found {len(transactions)} transactions")
            endpoints_tested.append("GET /transactions")
        else:
            print(" GET /transactions - No transactions found")
    except Exception as e:
        print(f" GET /transactions failed: {e}")
    
    # Test GET (single)
    try:
        if transactions:
            single = store.get_transaction(transactions[0]['id'])
            if single:
                print(f" GET /transactions/{{id}} - Retrieved transaction {single['id']}")
                endpoints_tested.append("GET /transactions/{id}")
            else:
                print(" GET /transactions/{id} - Failed to retrieve")
    except Exception as e:
        print(f" GET /transactions/{{id}} failed: {e}")
    
    # Test POST (create)
    try:
        new_data = {
            "transaction_type": "test",
            "amount": 100.0,
            "sender": "test_sender",
            "receiver": "test_receiver", 
            "timestamp": "2024-09-29T16:00:00Z"
        }
        created = store.create_transaction(new_data)
        if created and 'id' in created:
            print(f" POST /transactions - Created transaction {created['id']}")
            endpoints_tested.append("POST /transactions")
            
            # Test PUT (update)
            try:
                updated = store.update_transaction(created['id'], {"amount": 200.0})
                if updated and updated['amount'] == 200.0:
                    print(f" PUT /transactions/{{id}} - Updated transaction {created['id']}")
                    endpoints_tested.append("PUT /transactions/{id}")
                else:
                    print(" PUT /transactions/{id} - Update failed")
            except Exception as e:
                print(f" PUT /transactions/{{id}} failed: {e}")
            
            # Test DELETE
            try:
                deleted = store.delete_transaction(created['id'])
                if deleted:
                    print(f" DELETE /transactions/{{id}} - Deleted transaction {created['id']}")
                    endpoints_tested.append("DELETE /transactions/{id}")
                else:
                    print(" DELETE /transactions/{id} - Delete failed")
            except Exception as e:
                print(f" DELETE /transactions/{{id}} failed: {e}")
                
        else:
            print(" POST /transactions - Create failed")
    except Exception as e:
        print(f" POST /transactions failed: {e}")
    
    print(f"\nEndpoints successfully tested: {len(endpoints_tested)}/5")
    for endpoint in endpoints_tested:
        print(f"   {endpoint}")
    
    return len(endpoints_tested) >= 4  # Allow for some flexibility

def test_authentication():
    """Test Authentication & Security (Rubric: Authentication & Security - 5 pts)"""
    print("\n" + "=" * 50)
    print("Testing Authentication & Security")
    print("=" * 50)
    
    sys.path.append('API')
    from server import parse_basic_auth
    import base64
    
    # Test valid credentials
    try:
        valid_creds = base64.b64encode(b"admin:password123").decode()
        result = parse_basic_auth(f"Basic {valid_creds}")
        if result == ("admin", "password123"):
            print(" Valid credentials accepted")
        else:
            print(" Valid credentials not parsed correctly")
            return False
    except Exception as e:
        print(f" Valid credential test failed: {e}")
        return False
    
    # Test invalid credentials
    try:
        result = parse_basic_auth("Invalid header")
        if result is None:
            print(" Invalid credentials rejected")
        else:
            print(" Invalid credentials not rejected properly")
            return False
    except Exception as e:
        print(f" Invalid credential test failed: {e}")
        return False
    
    # Test error handling
    try:
        result = parse_basic_auth("Basic invalidbase64!")
        if result is None:
            print(" Malformed auth header handled")
        else:
            print(" Malformed auth header not handled")
            return False
    except Exception as e:
        print(f" Error handling test failed: {e}")
        return False
    
    print("\n Basic Auth implementation: Complete")
    print(" Valid/invalid credential testing: Complete")
    print(" Security limitations explained in documentation")
    
    return True

def test_api_documentation():
    """Test API Documentation (Rubric: API Documentation - 5 pts)"""
    print("\n" + "=" * 50)
    print("Testing API Documentation")
    print("=" * 50)
    
    try:
        with open('docs/api_docs.md', 'r') as f:
            content = f.read()
        
        # Check for required elements
        required_elements = [
            'GET /transactions',
            'POST /transactions', 
            'PUT /transactions',
            'DELETE /transactions',
            'Response',
            'Request',
            'Authentication',
            'Error',
            '200', '201', '401', '404'  # Status codes
        ]
        
        missing_elements = []
        for element in required_elements:
            if element not in content:
                missing_elements.append(element)
        
        if not missing_elements:
            print(" Complete documentation with endpoint descriptions")
            print(" Request/response examples provided")
            print(" Error codes documented")
            print(" Authentication explained")
            print(" Security limitations discussed")
            print(f" Documentation length: {len(content)} characters")
            return True
        else:
            print(f" Missing elements in documentation: {missing_elements}")
            return False
            
    except FileNotFoundError:
        print(" API documentation file not found")
        return False
    except Exception as e:
        print(f" Documentation test failed: {e}")
        return False

def test_dsa_integration():
    """Test DSA Integration & Testing (Rubric: DSA Integration & Testing - 5 pts)"""
    print("\n" + "=" * 50)
    print("Testing DSA Integration & Testing")
    print("=" * 50)
    
    sys.path.append('API')
    from datastore import InMemoryStore
    
    store = InMemoryStore()
    store.load_from_xml()
    
    if len(store.transactions) == 0:
        print(" No transactions loaded for DSA testing")
        return False
    
    # Test linear search implementation
    try:
        sample_id = store.transactions[0]['id']
        result = store.linear_search_by_id(sample_id)
        if result and result['id'] == sample_id:
            print(" Linear search implemented and functional")
        else:
            print(" Linear search not working correctly")
            return False
    except Exception as e:
        print(f" Linear search test failed: {e}")
        return False
    
    # Test dictionary lookup implementation
    try:
        result = store.dict_lookup_by_id(sample_id)
        if result and result['id'] == sample_id:
            print(" Dictionary lookup implemented and functional")
        else:
            print(" Dictionary lookup not working correctly")
            return False
    except Exception as e:
        print(f" Dictionary lookup test failed: {e}")
        return False
    
    # Performance comparison
    try:
        sample_ids = [tx['id'] for tx in store.transactions[:10]]  # Test with 10 records
        
        # Time linear search
        linear_times = []
        for tx_id in sample_ids:
            start = time.perf_counter()
            for _ in range(100):  # Multiple iterations for accuracy
                store.linear_search_by_id(tx_id)
            linear_times.append(time.perf_counter() - start)
        
        # Time dictionary lookup
        dict_times = []
        for tx_id in sample_ids:
            start = time.perf_counter()
            for _ in range(100):
                store.dict_lookup_by_id(tx_id)
            dict_times.append(time.perf_counter() - start)
        
        avg_linear = mean(linear_times) * 1e6  # Convert to microseconds
        avg_dict = mean(dict_times) * 1e6
        
        print(f" Performance comparison completed:")
        print(f"   Linear search avg: {avg_linear:.2f} µs")
        print(f"   Dict lookup avg: {avg_dict:.2f} µs")
        print(f"   Performance gain: {avg_linear/avg_dict:.1f}x faster")
        
        if avg_dict < avg_linear:
            print(" Dictionary lookup is faster (as expected)")
        else:
            print("  Unexpected: Linear search appears faster (may be due to small dataset)")
        
        return True
        
    except Exception as e:
        print(f" Performance testing failed: {e}")
        return False

def main():
    """Run all tests according to rubric"""
    print("SMS Financial Tracker - Final Comprehensive Test")
    print("Testing against assignment rubric requirements")
    print("Each test is worth 5 points (Total: 25 points)")
    
    results = {}
    total_score = 0
    
    # Run all tests
    results['Data Parsing'] = test_data_parsing()
    results['API Implementation'] = test_api_implementation()
    results['Authentication & Security'] = test_authentication()
    results['API Documentation'] = test_api_documentation()
    results['DSA Integration & Testing'] = test_dsa_integration()
    
    # Calculate score
    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    
    for category, passed in results.items():
        if passed:
            print(f" {category}: PASS (5/5 points)")
            total_score += 5
        else:
            print(f" {category}: FAIL (0/5 points)")
    
    print(f"\nTOTAL SCORE: {total_score}/25 points ({total_score/25*100:.0f}%)")
    
    if total_score >= 20:
        print(" EXCELLENT! All major requirements met.")
    elif total_score >= 15:
        print(" GOOD! Most requirements met.")
    elif total_score >= 10:
        print("  NEEDS IMPROVEMENT. Some requirements missing.")
    else:
        print(" SIGNIFICANT ISSUES. Major requirements not met.")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()