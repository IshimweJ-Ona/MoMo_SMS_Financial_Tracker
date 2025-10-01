# Transactions API Documentation

Base URL: `http://127.0.0.1:8000`

Authentication: Basic Auth required on all endpoints.
- Username: `admin`
- Password: `password123`

## Endpoints

### GET /transactions
List all transactions.

Request:
```bash
curl -u admin:password123 http://127.0.0.1:8000/transactions
```

Response 200:
```json
[
  {
    "id": "1",
    "transaction_type": "deposit",
    "amount": 20.5,
    "sender": "alice",
    "receiver": "momo",
    "timestamp": "2024-09-01T10:00:00Z"
  }
]
```

Errors:
- 401 Unauthorized (missing/invalid credentials)

### GET /transactions/{id}
Retrieve a single transaction by id.

Request:
```bash
curl -u admin:password123 http://127.0.0.1:8000/transactions/1
```

Responses:
- 200 OK + JSON transaction
- 404 Not Found
- 401 Unauthorized

### POST /transactions
Create a new transaction.

Request:
```bash
curl -u admin:password123 -X POST http://127.0.0.1:8000/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_type": "withdrawal",
    "amount": 50.0,
    "sender": "momo",
    "receiver": "bob",
    "timestamp": "2024-09-01T12:00:00Z"
  }'
```

Responses:
- 201 Created + JSON transaction
- 400 Bad Request (malformed JSON)
- 401 Unauthorized

### PUT /transactions/{id}
Update fields on an existing transaction.

Request:
```bash
curl -u admin:password123 -X PUT http://127.0.0.1:8000/transactions/1 \
  -H "Content-Type: application/json" \
  -d '{ "amount": 75.25 }'
```

Responses:
- 200 OK + updated JSON transaction
- 404 Not Found
- 400 Bad Request (malformed JSON)
- 401 Unauthorized

### DELETE /transactions/{id}
Delete a transaction.

Request:
```bash
curl -u admin:password123 -X DELETE http://127.0.0.1:8000/transactions/1
```

Responses:
- 204 No Content
- 404 Not Found
- 401 Unauthorized

## Error Model
```json
{ "error": "message" }
```

## Notes on Security
- Basic Auth sends credentials base64-encoded, not encrypted. Use HTTPS to avoid credential interception.
- Prefer stronger alternatives in production:
  - JWT with short-lived tokens and refresh tokens.
  - OAuth2 with Authorization Code flow (PKCE) for third-party apps.
  - Mutual TLS for high-trust internal services.
