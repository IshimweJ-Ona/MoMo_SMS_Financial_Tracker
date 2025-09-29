import time
from data_parser import SMSDataParser

class SearchComparison:
    def __init__(self, transactions):
        self.transactions = transactions
        self.transactions_dict = {txn['id']: txn for txn in transactions}
    
    def linear_search(self, transaction_id):
        """Linear search implementation - O(n) complexity"""
        start_time = time.time()
        for transaction in self.transactions:
            if transaction['id'] == transaction_id:
                return transaction, time.time() - start_time
        return None, time.time() - start_time
    
    def dictionary_lookup(self, transaction_id):
        """Dictionary lookup implementation - O(1) complexity"""
        start_time = time.time()
        transaction = self.transactions_dict.get(transaction_id)
        return transaction, time.time() - start_time
    
    def compare_search_methods(self, search_ids):
        """Compare linear search vs dictionary lookup"""
        print("Comparing Search Algorithms...\n")
        
        results = []
        
        for search_id in search_ids:
            # Linear Search
            linear_result, linear_time = self.linear_search(search_id)
            
            # Dictionary Lookup
            dict_result, dict_time = self.dictionary_lookup(search_id)
            
            results.append({
                'search_id': search_id,
                'linear_search_time': linear_time,
                'dictionary_lookup_time': dict_time,
                'speedup': linear_time / dict_time if dict_time > 0 else float('inf')
            })
            
            print(f"Transaction ID {search_id}:")
            print(f"  Linear Search: {linear_time:.6f} seconds")
            print(f"  Dictionary Lookup: {dict_time:.6f} seconds")
            print(f"  Speedup: {linear_time/dict_time if dict_time > 0 else 'N/A':.2f}x")
            print()
        
        return results
    
    def generate_report(self):
        """Generate comprehensive DSA report"""
        # Test with at least 20 records
        test_ids = [txn['id'] for txn in self.transactions[:20]]
        
        print("=" * 50)
        print("DSA SEARCH ALGORITHM ANALYSIS REPORT")
        print("=" * 50)
        
        print(f"Total transactions in dataset: {len(self.transactions)}")
        print(f"Testing with: {len(test_ids)} records")
        print()
        
        results = self.compare_search_methods(test_ids)
        
        # Summary statistics
        total_linear_time = sum(r['linear_search_time'] for r in results)
        total_dict_time = sum(r['dictionary_lookup_time'] for r in results)
        avg_speedup = total_linear_time / total_dict_time if total_dict_time > 0 else 0
        
        print("PERFORMANCE SUMMARY:")
        print(f"Total Linear Search Time: {total_linear_time:.6f} seconds")
        print(f"Total Dictionary Lookup Time: {total_dict_time:.6f} seconds")
        print(f"Average Speedup: {avg_speedup:.2f}x faster")
        print()
        
        print("WHY DICTIONARY LOOKUP IS FASTER:")
        print("• Linear Search: O(n) time complexity - checks each element one by one")
        print("• Dictionary Lookup: O(1) average case - direct access via hash table")
        print("• Hash tables use mathematical functions to compute memory locations")
        print()
        
        print("ALTERNATIVE DATA STRUCTURES FOR IMPROVEMENT:")
        print("1. Binary Search Tree (BST): O(log n) search time, maintains order")
        print("2. B-Trees: Efficient for large datasets stored on disk")
        print("3. Hash Tables with Better Hash Functions: Reduce collisions")
        print("4. Bloom Filters: Probabilistic data structure for membership testing")
        print("5. Trie: Excellent for prefix-based searches (not applicable here)")
        print()
        
        print("RECOMMENDATION:")
        print("For this use case, Dictionary/Hash Table is optimal because:")
        print("• We need fast lookups by transaction ID")
        print("• Memory usage is acceptable for the dataset size")
        print("• No need for ordered traversal of transactions")

def main():
    # Parse data
    parser = SMSDataParser('modified_sms_v2.xml')
    transactions = parser.parse_xml()
    
    if not transactions:
        print("No transactions found. Please check your XML file.")
        return
    
    # Run analysis
    comparator = SearchComparison(transactions)
    comparator.generate_report()

if __name__ == '__main__':
    main()