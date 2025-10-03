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
        "transaction_id": "73214484437",
        "transaction_type": "payment",
        "amount": 1000.0,
        "sender": "You",
        "receiver": "Jane Smith",
        "timestamp": "2024-05-10T16:31:46.754000",
        "status": "completed",
        "raw_message": "TxId: 73214484437. Your payment of 1,000 RWF to Jane Smith 12845 has been completed at 2024-05-10 16:31:39. Your new balance: 1,000 RWF. Fee was 0 RWF.Kanda*182*16# wiyandikishe muri poromosiyo ya BivaMoMotima, ugire amahirwe yo gutsindira ibihembo bishimishije.",
        "created_at": "2025-10-03T12:51:45.218307"
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
  "id": "941",
  "transaction_id": "1000",
  "transaction_type": "transfer",
  "amount": 40000.0,
  "sender": "You",
  "receiver": "Samuel Junior",
  "timestamp": "2024-05-21T14:38:21.885000",
  "status": "completed",
  "raw_message": "*165*5*1500 RWF transferred to Samuel Carter (250791666666) from 36521838 at 2024-05-21 14:38:14. Fee was: 100 RWF. New balance: 33350 RWF. Kugura ama inite cg interneti kuri MoMo, Kanda *182*2*1# .*EN#",
  "created_at": "2025-10-02T15:48:19.242339",
  "updated_at": ""
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
- 200 Transaction {id} deleted successfuly

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
