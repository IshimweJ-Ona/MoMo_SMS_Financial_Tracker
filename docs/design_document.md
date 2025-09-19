# MoMo SMS Financial Tracker - Design Document

## Entity Relationship Diagram (ERD)
[ERD image placeholder - to be added]

## Design Justification

This financial tracking system is designed to capture and manage Mobile Money (MoMo) transactions from SMS messages. The database schema prioritizes data integrity, auditability, and scalability for financial operations.

The four-table design separates concerns: Users store customer information, Transaction_Categories provide transaction type classification, Transactions capture the core financial data with proper relationships, and System_Logs ensure complete audit trails for compliance and debugging.

Foreign key constraints ensure referential integrity, while the decimal precision for amounts prevents rounding errors in financial calculations. The unique phone number constraint prevents duplicate user accounts, and the comprehensive logging system supports regulatory compliance requirements.

## Data Dictionary

### Table: Users
- **user_id** INT PK AUTO_INCREMENT: Primary key, unique identifier
- **name** VARCHAR(100): Full name of the user
- **phone** VARCHAR(20) UNIQUE: Phone number used in MoMo (unique constraint)
- **email** VARCHAR(100): Optional user email address

### Table: Transaction_Categories
- **category_id** INT PK AUTO_INCREMENT: Primary key, unique identifier
- **category_name** VARCHAR(50): Name of transaction category
- **description** VARCHAR(255): Detailed description of the category

### Table: Transactions
- **transaction_id** INT PK AUTO_INCREMENT: Primary key, unique identifier
- **sender_id** INT FK: References Users.user_id (sender)
- **receiver_id** INT FK: References Users.user_id (receiver)
- **amount** DECIMAL(12,2): Transaction amount (precision for financial data)
- **txn_date** DATETIME: Transaction timestamp
- **category_id** INT FK: References Transaction_Categories.category_id
- **status** VARCHAR(30): Transaction status (completed, pending, failed, etc.)
- **raw_message** TEXT: Original SMS message content

### Table: System_Logs
- **log_id** INT PK AUTO_INCREMENT: Primary key, unique identifier
- **transaction_id** INT FK: References Transactions.transaction_id
- **action** VARCHAR(100): Action performed (INSERT, UPDATE, DELETE)
- **timestamp** DATETIME: Log entry timestamp (auto-generated)
- **notes** TEXT: Additional log information

## Security and Validation Rules

### Foreign Key Constraints
- All foreign key relationships are enforced for referential integrity
- Cascade rules prevent orphaned records

### Data Validation
- Amount must be positive (enforced at application level)
- Phone numbers are unique across all users
- Email format validation (enforced at application level)

### Index Recommendations
```sql
CREATE INDEX idx_txn_date ON Transactions(txn_date);
CREATE INDEX idx_user_phone ON Users(phone);
CREATE INDEX idx_txn_status ON Transactions(status);
```

## Sample Queries

### SELECT Operations
```sql
-- All users
SELECT * FROM Users;

-- All transaction categories
SELECT * FROM Transaction_Categories;

-- Recent transactions
SELECT * FROM Transactions LIMIT 10;

-- System logs
SELECT * FROM System_Logs;
```

### INSERT Operations
```sql
-- Add new user
INSERT INTO Users (name, phone) VALUES ('Frank','0788000006');
```

### UPDATE Operations
```sql
-- Update transaction status
UPDATE Transactions SET status = 'reconciled' WHERE transaction_id = 1;
```

### DELETE Operations
```sql
-- Remove user
DELETE FROM Users WHERE phone = '0788000006';
```

## Performance Considerations

- Index on transaction_date for time-based queries
- Index on user phone for quick lookups
- Index on transaction status for filtering
- Consider partitioning for large transaction volumes

## Compliance and Audit

- Complete audit trail in System_Logs table
- Timestamp tracking for all operations
- Immutable log entries for regulatory compliance
- Data retention policies can be implemented based on timestamps
