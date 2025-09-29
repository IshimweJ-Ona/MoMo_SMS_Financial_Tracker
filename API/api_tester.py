import requests
import base64
import json

class APITester:
    def __init__(self, base_url='http://localhost:8000'):
        self.base_url = base_url
    
    def _get_auth_header(self, username, password):
        credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
        return {'Authorization': f'Basic {credentials}'}
    
    def test_all_endpoints(self):
        """Test all API endpoints"""
        print("=== Testing SMS Transactions API ===\n")
        
        # Test 1: Unauthorized access
        print("1. Testing unauthorized access...")
        wrong_auth = self._get_auth_header('wrong', 'credentials')
        response = requests.get(f"{self.base_url}/transactions", headers=wrong_auth)
        print(f"   Status: {response.status_code} - {response.json()}\n")
        
        # Test 2: Get all transactions (authorized)
        print("2. Testing GET /transactions (authorized)...")
        auth_header = self._get_auth_header('admin', 'password123')
        response = requests.get(f"{self.base_url}/transactions", headers=auth_header)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Retrieved {len(data)} transactions\n")
        
        # Test 3: Get single transaction
        print("3. Testing GET /transactions/1...")
        response = requests.get(f"{self.base_url}/transactions/1", headers=auth_header)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Transaction: {json.dumps(response.json(), indent=2)}\n")
        
        # Test 4: Create new transaction
        print("4. Testing POST /transactions...")
        new_transaction = {
            "address": "TEST123",
            "body": "You sent 200.00 to 254711223344",
            "transaction_type": "sent",
            "amount": 200.00,
            "sender": "You",
            "receiver": "254711223344"
        }
        response = requests.post(
            f"{self.base_url}/transactions",
            headers={**auth_header, 'Content-Type': 'application/json'},
            data=json.dumps(new_transaction)
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 201:
            created = response.json()
            print(f"   Created transaction ID: {created['id']}\n")
            
            # Test 5: Update transaction
            print("5. Testing PUT /transactions/{new_id}...")
            update_data = {"amount": 250.00}
            response = requests.put(
                f"{self.base_url}/transactions/{created['id']}",
                headers={**auth_header, 'Content-Type': 'application/json'},
                data=json.dumps(update_data)
            )
            print(f"   Status: {response.status_code}")
            
            # Test 6: Delete transaction
            print("6. Testing DELETE /transactions/{new_id}...")
            response = requests.delete(
                f"{self.base_url}/transactions/{created['id']}",
                headers=auth_header
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   Response: {response.json()}\n")

if __name__ == '__main__':
    tester = APITester()
    tester.test_all_endpoints()