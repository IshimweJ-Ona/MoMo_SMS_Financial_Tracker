#!/bin/bash
# MoMo SMS Financial Tracker - Demo Script
# Run this during your presentation to show your database working

echo "=== MoMo SMS Financial Tracker Demo ==="
echo "This shows my database system working"
echo

echo "1. Showing all users in my database:"
sudo mysql --defaults-file=/etc/mysql/debian.cnf -D momo_tracker -e "SELECT user_id, name, phone FROM Users;"
echo

echo "2. Showing transaction categories:"
sudo mysql --defaults-file=/etc/mysql/debian.cnf -D momo_tracker -e "SELECT cat_id, cat_name FROM Transaction_Categories;"
echo

echo "3. Showing recent transactions:"
sudo mysql --defaults-file=/etc/mysql/debian.cnf -D momo_tracker -e "SELECT txn_id, amount, txn_date, status FROM Transactions ORDER BY txn_date DESC LIMIT 5;"
echo

echo "4. Showing how tables are connected (who sent money to whom):"
sudo mysql --defaults-file=/etc/mysql/debian.cnf -D momo_tracker -e "SELECT 
    sender.name as 'Sender', 
    receiver.name as 'Receiver', 
    t.amount as 'Amount', 
    tc.cat_name as 'Category'
FROM Transactions t
JOIN Users sender ON t.sender_id = sender.user_id
JOIN Users receiver ON t.receiver_id = receiver.user_id
JOIN Transaction_Categories tc ON t.category_id = tc.cat_id
ORDER BY t.txn_date DESC LIMIT 5;"
echo

echo "5. Showing system logs (audit trail):"
sudo mysql --defaults-file=/etc/mysql/debian.cnf -D momo_tracker -e "SELECT log_id, txn_id, action, timestamp FROM System_Logs ORDER BY timestamp DESC LIMIT 5;"
echo

echo "6. Testing data validation (trying to add invalid data):"
echo "   Trying to add negative amount (should fail):"
sudo mysql --defaults-file=/etc/mysql/debian.cnf -D momo_tracker -e "INSERT INTO Transactions (sender_id, receiver_id, amount, txn_date) VALUES (1, 2, -100, NOW());" 2>&1 | head -1
echo

echo "7. Showing database statistics:"
sudo mysql --defaults-file=/etc/mysql/debian.cnf -D momo_tracker -e "SELECT 
    'Users' as 'Table', COUNT(*) as 'Records' FROM Users
UNION ALL
SELECT 'Transactions', COUNT(*) FROM Transactions
UNION ALL
SELECT 'Categories', COUNT(*) FROM Transaction_Categories
UNION ALL
SELECT 'Logs', COUNT(*) FROM System_Logs;"
echo

echo "=== Demo Complete ==="
echo "This shows my database is working correctly with all the features I built!"
