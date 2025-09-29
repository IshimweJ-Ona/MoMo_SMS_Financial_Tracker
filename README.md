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

## Running the local API

1) Start the server

```bash
python -m api.server
```

The server will load `api/modified_sms_v2.xml` via the datastore, parse it into transactions, and expose CRUD endpoints.

2) Authentication (Basic Auth)

- Username: `admin`
- Password: `password123`

Send the `Authorization: Basic <base64(admin:password123)>` header with requests. Invalid or missing credentials return `401` with `WWW-Authenticate` header.

Limitations: Basic Auth sends credentials with each request and is not encrypted by itself. Use HTTPS in production, rotate credentials, and prefer token-based auth for stronger security.

3) Endpoints

- GET `/transactions` → 200 OK, returns array of transactions
- GET `/transactions/{id}` → 200 OK with object, or 404 if not found
- POST `/transactions` → 201 Created, body fields: `transaction_type` (str), `amount` (number), `sender` (str), `receiver` (str), `timestamp` (ISO str). Returns created object with `id`.
- PUT `/transactions/{id}` → 200 OK with updated object, or 404 if not found
- DELETE `/transactions/{id}` → 204 No Content on success, 404 if not found

4) Errors

- 400 Bad Request: Malformed JSON body
- 401 Unauthorized: Missing/invalid Basic Auth
- 404 Not Found: Unknown route or missing resource

## Data Ingestion from XML

- Source file: `api/modified_sms_v2.xml` (1693 messages)
- Parser: `api/data_parser.py` (`SMSDataParser`)
- Store: `api/datastore.py` loads XML on first run and caches to `api/transactions.json` for faster subsequent loads.

Key parsed fields per transaction:
- `id` (from SMS or auto-generated)
- `transaction_type` (`received`, `sent`, `withdrawal`, `deposit`, `unknown`)
- `amount` (float)
- `sender`, `receiver` (best-effort extraction from SMS body)
- `timestamp` (ISO 8601 when convertible)

## DSA Integration & Testing

Two lookup methods are implemented in `api/datastore.py`:
- Linear search: `linear_search_by_id`
- Dictionary lookup: `dict_lookup_by_id`

To run the comparison test:

```bash
python -m dsa.dsa_compare
```

This prints average timings for 20 sample IDs, demonstrating dictionary lookup is faster (O(1) average) than linear search (O(n)).

## API Test Script

Use the helper tester to validate endpoints and auth flows:

```bash
python -m api.api_tester
```

It verifies: unauthorized access handling, list/get, create, update, and delete flows end-to-end.

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

## System Architecture
We used a web application 'Draw.io' to construct the functionality of the app
The diagram illustrates full data flow from APIs and SMS XML ingestion to frontend visualisation.
--Link to the architecture diagram
 [https://drive.google.com/file/d/1HsT7zy_rY5yrXu_hj6QoLXynkAvLYqsi/view?usp=sharing]

## ERD Diagram Design
[https://drive.google.com/file/d/1C4vF6A7KHkcdj6qKuPrMPtjd5aZPzCfP/view?ts=68cd1754]

## Scrum Board
[https://alustudent-team-pch2djpv.atlassian.net/jira/software/projects/SCRUM/boards/1?atlOrigin=eyJpIjoiNTdiNTU5YTJiNzEyNDJiYzk0MmQxOTQ3M2YwNzVjZWYiLCJwIjoiaiJ9]
