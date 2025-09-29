import time
from API.simple_data_parser import SimpleDataParser

class SimpleDSAComparison:
    """Simple comparison between linear search and dictionary lookup - Beginner friendly"""
    
    def __init__(self, transactions):
        print("Setting up data structures for comparison...")
        
        # Store transactions as a list (for linear search)
        self.transaction_list = transactions
        
        # Store transactions as a dictionary (for fast lookup)
        self.transaction_dict = {}
        for transaction in transactions:
            transaction_id = transaction['id']
            self.transaction_dict[transaction_id] = transaction
        
        print(f"Loaded {len(transactions)} transactions")
    
    def linear_search_method(self, search_id):
        """Method 1: Linear Search - Go through each item one by one until we find it"""
        # Record start time
        start_time = time.time()
        
        # Look through each transaction in the list
        found_transaction = None
        for transaction in self.transaction_list:
            if transaction['id'] == search_id:
                found_transaction = transaction
                break  # Stop looking once we found it
        
        # Calculate how long it took
        search_time = time.time() - start_time
        
        return found_transaction, search_time
    
    def dictionary_lookup_method(self, search_id):
        """Method 2: Dictionary Lookup - Jump directly to the item we want"""
        # Record start time
        start_time = time.time()
        
        # Look up the transaction directly using its ID as a key
        found_transaction = self.transaction_dict.get(search_id)
        
        # Calculate how long it took
        search_time = time.time() - start_time
        
        return found_transaction, search_time
    
    def compare_both_methods(self, test_ids):
        """Compare both methods and show which is faster"""
        print("\\n" + "="*60)
        print("COMPARING TWO SEARCH METHODS")
        print("="*60)
        
        print("Method 1: Linear Search (check each item one by one)")
        print("Method 2: Dictionary Lookup (jump directly to the item)")
        print()
        
        total_linear_time = 0
        total_dict_time = 0
        
        for search_id in test_ids:
            print(f"Looking for transaction ID {search_id}...")
            
            # Test Method 1: Linear Search
            result1, time1 = self.linear_search_method(search_id)
            total_linear_time += time1
            
            # Test Method 2: Dictionary Lookup
            result2, time2 = self.dictionary_lookup_method(search_id)
            total_dict_time += time2
            
            # Show results
            if time2 > 0:
                speed_difference = time1 / time2
                print(f"  Linear Search:     {time1*1000000:.2f} microseconds")
                print(f"  Dictionary Lookup: {time2*1000000:.2f} microseconds")
                print(f"  → Dictionary is {speed_difference:.1f}x faster!")
            print()
        
        # Summary
        print("FINAL RESULTS:")
        print(f"Total Linear Search time:     {total_linear_time*1000000:.2f} microseconds")
        print(f"Total Dictionary Lookup time: {total_dict_time*1000000:.2f} microseconds")
        
        if total_dict_time > 0:
            overall_speedup = total_linear_time / total_dict_time
            print(f"Overall speedup: Dictionary is {overall_speedup:.1f}x faster!")
        
        print("\\nWHY IS DICTIONARY LOOKUP FASTER?")
        print("Linear Search:")
        print("  • Checks item 1, then item 2, then item 3... until found")
        print("  • If item is at position 50, needs to check 50 times")
        print("  • Time increases with more data (O(n) complexity)")
        
        print("\\nDictionary Lookup:")
        print("  • Uses a 'hash table' to calculate where item should be")
        print("  • Jumps directly to that location")
        print("  • Time stays the same regardless of data size (O(1) complexity)")
        
        print("\\nREAL WORLD EXAMPLE:")
        print("Linear Search = Reading a book page by page to find a word")
        print("Dictionary Lookup = Using the index to jump to the right page")
        
        return {
            'linear_total_time': total_linear_time,
            'dict_total_time': total_dict_time,
            'speedup': total_linear_time / total_dict_time if total_dict_time > 0 else 0
        }

def main():
    """Main function to run the DSA comparison"""
    print("Starting Simple DSA Performance Test")
    print("="*50)
    
    # Load transaction data
    print("Loading transaction data from XML...")
    parser = SimpleDataParser('API/modified_sms_v2.xml')
    transactions = parser.parse_xml()
    
    if not transactions:
        print("No transactions found! Please check your XML file.")
        return
    
    # Set up comparison
    comparison = SimpleDSAComparison(transactions)
    
    # Pick some transaction IDs to test with
    test_ids = []
    for i in range(min(10, len(transactions))):  # Test with first 10 transactions
        test_ids.append(transactions[i]['id'])
    
    print(f"Testing with {len(test_ids)} different transaction IDs...")
    
    # Run the comparison
    results = comparison.compare_both_methods(test_ids)
    
    print("\\nTest completed successfully!")
    print(f"Dictionary lookup was {results['speedup']:.1f}x faster than linear search")

if __name__ == '__main__':
    main()