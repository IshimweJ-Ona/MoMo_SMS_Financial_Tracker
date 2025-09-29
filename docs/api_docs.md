# SMS Financial Tracker API Documentation

## Overview
RESTful API for managing SMS-based financial transaction data from MoMo (Mobile Money) services. This API provides CRUD operations on parsed transaction data with Basic Authentication security.

**Base URL:** `http://127.0.0.1:8000`

**Authentication:** Basic Auth required on all endpoints
- Username: `admin`
- Password: `password123`

## Data Model

### Transaction Object
```json
{
  "id": "string",
  "transaction_type": "send|receive|deposit|airtime|other",
  "amount": number,
  "sender": "string",
  "receiver": "string",
  "timestamp": "ISO 8601 datetime",
  "original_body": "string (optional - SMS body excerpt)"
}
```

## API Endpoints

### GET /transactions
Retrieve all transactions.

**Request:**
```bash
curl -u admin:password123 http://127.0.0.1:8000/transactions
```

**Response 200 OK:**
```json
[
  {
    "id": "1",
    "transaction_type": "receive",
    "amount": 2000.0,
    "sender": "Jane Smith",
    "receiver": "me",
    "timestamp": "2024-05-10T16:31:46Z",
    "original_body": "You have received 2000 RWF from Jane Smith (*********013) on your mobile money account..."
  },
  {
    "id": "2",
    "transaction_type": "deposit",
    "amount": 5000.0,
    "sender": "bank",
    "receiver": "me",
    "timestamp": "2024-05-14T09:12:08Z",
    "original_body": "*113*R*A bank deposit of 5000 RWF has been added to your mobile money account..."
  }
]
```

**Errors:**
- `401 Unauthorized` - Missing or invalid credentials

### GET /transactions/{id}
Retrieve a single transaction by ID.

**Request:**
```bash
curl -u admin:password123 http://127.0.0.1:8000/transactions/1
```

**Response 200 OK:**
```json
{
  "id": "1",
  "transaction_type": "receive",
  "amount": 2000.0,
  "sender": "Jane Smith",
  "receiver": "me",
  "timestamp": "2024-05-10T16:31:46Z",
  "original_body": "You have received 2000 RWF from Jane Smith..."
}
```

**Errors:**
- `404 Not Found` - Transaction ID does not exist
- `401 Unauthorized` - Missing or invalid credentials

### POST /transactions
Create a new transaction.

**Request:**
```bash
curl -u admin:password123 -X POST http://127.0.0.1:8000/transactions \\
  -H "Content-Type: application/json" \\
  -d '{
    "transaction_type": "send",
    "amount": 1500.0,
    "sender": "me",
    "receiver": "John Doe",
    "timestamp": "2024-09-29T16:00:00Z"
  }'
```

**Response 201 Created:**
```json
{
  "id": "98",
  "transaction_type": "send",
  "amount": 1500.0,
  "sender": "me",
  "receiver": "John Doe",
  "timestamp": "2024-09-29T16:00:00Z"
}
```

**Errors:**
- `400 Bad Request` - Malformed JSON or missing required fields
- `401 Unauthorized` - Missing or invalid credentials

### PUT /transactions/{id}
Update fields on an existing transaction. Only provided fields are updated.

**Request:**
```bash
curl -u admin:password123 -X PUT http://127.0.0.1:8000/transactions/1 \\
  -H "Content-Type: application/json" \\
  -d '{
    "amount": 2500.0,
    "sender": "Updated Sender"
  }'
```

**Response 200 OK:**
```json
{
  "id": "1",
  "transaction_type": "receive",
  "amount": 2500.0,
  "sender": "Updated Sender",
  "receiver": "me",
  "timestamp": "2024-05-10T16:31:46Z",
  "original_body": "You have received 2000 RWF from Jane Smith..."
}
```

**Errors:**
- `404 Not Found` - Transaction ID does not exist
- `400 Bad Request` - Malformed JSON
- `401 Unauthorized` - Missing or invalid credentials

### DELETE /transactions/{id}
Delete a transaction permanently.

**Request:**
```bash
curl -u admin:password123 -X DELETE http://127.0.0.1:8000/transactions/1
```

**Response 204 No Content:**
```
(Empty response body)
```

**Errors:**
- `404 Not Found` - Transaction ID does not exist
- `401 Unauthorized` - Missing or invalid credentials

## Error Response Format
```json
{
  "error": "Error description message"
}
```

## HTTP Status Codes
- `200 OK` - Successful GET/PUT request
- `201 Created` - Successful POST request
- `204 No Content` - Successful DELETE request
- `400 Bad Request` - Invalid request format or data
- `401 Unauthorized` - Authentication required or invalid credentials
- `404 Not Found` - Resource does not exist

## Authentication & Security

### Current Implementation
- **Basic Authentication** with hardcoded credentials
- Username: `admin`
- Password: `password123`
- Credentials sent as base64-encoded string in `Authorization` header

### Security Limitations
1. **Plaintext transmission**: Basic Auth credentials are only base64-encoded, not encrypted
2. **Static credentials**: No user management or credential rotation
3. **Session persistence**: Credentials required on every request
4. **No HTTPS**: Vulnerable to man-in-the-middle attacks

### Recommended Production Alternatives
1. **JWT (JSON Web Tokens)**
   - Short-lived access tokens with refresh mechanism
   - Stateless authentication
   - Token-based authorization with scopes

2. **OAuth2 with PKCE**
   - Industry standard for API security
   - Support for third-party applications
   - Fine-grained permission control

3. **Mutual TLS (mTLS)**
   - Certificate-based authentication
   - Ideal for service-to-service communication
   - Strong cryptographic security

## DSA Performance Analysis

The API implements two search methods for educational comparison:

### Linear Search
- **Time Complexity**: O(n)
- **Average Time**: ~3.76 microseconds (for 97 transactions)
- **Use Case**: Small datasets, simple implementation

### Dictionary Lookup
- **Time Complexity**: O(1) average case
- **Average Time**: ~0.94 microseconds (for 97 transactions)
- **Use Case**: Large datasets, frequent lookups
- **Performance Gain**: ~4x faster than linear search

### Conclusion
Dictionary lookup provides significant performance benefits for transaction retrieval operations, especially as the dataset grows.
