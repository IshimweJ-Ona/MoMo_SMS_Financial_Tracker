# Entity Relationship Diagram (ERD)

## MoMo SMS Financial Tracker Database Schema

Based on the provided ERD design:

```
┌─────────────────┐    ┌──────────────────────┐    ┌─────────────────┐
│     Users       │    │ Transaction_Categories│    │   Transactions  │
├─────────────────┤    ├──────────────────────┤    ├─────────────────┤
│ user_id (PK)    │    │ cat_id (PK)          │    │ txn_id (PK)     │
│ name            │    │ cat_name             │    │ sender_id (FK)  │
│ phone           │    │ description          │    │ receiver_id (FK)│
│ email           │    └──────────────────────┘    │ amount          │
└─────────────────┘              │                 │ txn_date        │
         │                        │                 │ category_id (FK)│
         │                        │                 │ status          │
         │                        │                 └─────────────────┘
         │                        │                          │
         │                        └──────────────────────────┘
         │
         │
         │
┌─────────────────┐
│  System_Logs    │
├─────────────────┤
│ log_id (PK)     │
│ txn_id (FK)     │
│ action          │
│ timestamp       │
└─────────────────┘
```

## Relationships (as per your ERD):

### Users → Transactions (Sender)
- **Relationship**: One-to-Many
- **Description**: One user can be a sender of multiple transactions
- **Foreign Key**: `Transactions.sender_id` → `Users.user_id`

### Users → Transactions (Receiver)  
- **Relationship**: One-to-Many
- **Description**: One user can be a receiver of multiple transactions
- **Foreign Key**: `Transactions.receiver_id` → `Users.user_id`

### Transaction_Categories → Transactions
- **Relationship**: One-to-Many
- **Description**: One category can be applied to multiple transactions
- **Foreign Key**: `Transactions.category_id` → `Transaction_Categories.cat_id`

### Transactions → System_Logs
- **Relationship**: One-to-Many
- **Description**: One transaction can have multiple log entries
- **Foreign Key**: `System_Logs.txn_id` → `Transactions.txn_id`

## Key Design Features:
- **Primary Keys**: All tables have auto-incrementing primary keys
- **Foreign Keys**: Maintain referential integrity across all relationships
- **Audit Trail**: Complete logging system via System_Logs table
- **Flexible Transactions**: Users can both send and receive transactions
- **Categorization**: All transactions are classified by category

## Database Constraints:
- Phone numbers are unique across users
- Amount values must be positive
- Status values are constrained to valid options
- All foreign key relationships are enforced
- Complete audit trail maintained for compliance
