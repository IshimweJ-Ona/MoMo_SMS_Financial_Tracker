# MoMo SMS Financial Tracker

## Team Members
- Gedeon NTIGIBESHYA
- Arnold Eloi Buyange Muvunyi 

## Description
A financial transaction tracking system for Mobile Money (MoMo) SMS messages. This project includes database schema, JSON API examples, and CRUD operations for managing financial transactions.

## Project Structure
```
MoMo_SMS_Financial_Tracker/
├── database/
│   └── database_setup.sql    # MySQL database schema and sample data
├── examples/
│   └── json_schemas.json     # API response examples
└── README.md
```

## Database Setup

### Prerequisites
- MySQL Server 8.0+

### Installation (Ubuntu/Pop!_OS)
```bash
sudo apt update
sudo apt install mysql-server
sudo systemctl start mysql
```

### Run Database Setup
```bash
# Using maintenance account (recommended)
sudo mysql --defaults-file=/etc/mysql/debian.cnf < database/database_setup.sql

# Or with root password (if configured)
mysql -u root -p < database/database_setup.sql
```

### Verify Installation
```bash
sudo mysql --defaults-file=/etc/mysql/debian.cnf -e "USE momo_tracker; SHOW TABLES;"
```

## Database Schema

### Tables
- **Users**: User information (name, phone, email)
- **Transaction_Categories**: Transaction types (Send Money, Withdraw, etc.)
- **Transactions**: Financial transactions with sender/receiver relationships
- **System_Logs**: Audit trail for transaction operations

### Key Features
- Foreign key constraints for data integrity
- Auto-incrementing primary keys
- Unique phone number constraint
- Decimal precision for monetary amounts
- Timestamp tracking for all operations

## JSON API Examples

See `examples/json_schemas.json` for sample API response structures showing how transaction data would be returned by the system.

## CRUD Operations

The database supports full CRUD operations:
- **CREATE**: Insert new users and transactions
- **READ**: Query users, transactions, and logs
- **UPDATE**: Modify transaction status and user information
- **DELETE**: Remove users and transactions

## Design Document

See the project documentation for:
- Entity Relationship Diagram (ERD)
- Data dictionary with column descriptions
- Security constraints and validation rules
- Index recommendations for performance

## Scrum Board
[Link to be added]

## License
MIT
