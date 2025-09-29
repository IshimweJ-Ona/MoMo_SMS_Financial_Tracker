# MoMo SMS Financial Tracker API

This project builds a simple REST API in plain Python (`http.server`) to expose parsed MoMo SMS transaction data, secured with Basic Auth. It also includes a small DSA comparison between linear search and dictionary lookup.

## Project Structure
- `data/modified_sms_v2.xml` — input dataset (place here)
- `dsa/parser.py` — XML -> JSON parser
- `api/datastore.py` — in-memory store (list + dict index) and CRUD
- `api/server.py` — HTTP API with Basic Auth
- `dsa/dsa_compare.py` — linear vs dict lookup timing
- `docs/api_docs.md` — endpoint docs with examples
- `screenshots/` — place testing screenshots

## Requirements
- Python 3.9+
- Windows PowerShell or any shell

## Setup
1. Put your dataset file at `data/modified_sms_v2.xml`.
2. Optionally pre-generate JSON for faster startup:
```bash
python dsa/parser.py
```
This writes `data/parsed_sms.json`.

## Run the API
```bash
python api/server.py
```
Server runs on `http://127.0.0.1:8000`.

Auth credentials:
- Username: `admin`
- Password: `password123`

## Test with curl
- List:
```bash
curl -u admin:password123 http://127.0.0.1:8000/transactions
```
- Unauthorized:
```bash
curl http://127.0.0.1:8000/transactions -i
```
- Create:
```bash
curl -u admin:password123 -X POST http://127.0.0.1:8000/transactions \
  -H "Content-Type: application/json" \
  -d '{"transaction_type":"deposit","amount":12.34,"sender":"alice","receiver":"momo","timestamp":"2024-09-01T10:00:00Z"}'
```
- Update:
```bash
curl -u admin:password123 -X PUT http://127.0.0.1:8000/transactions/1 \
  -H "Content-Type: application/json" -d '{"amount":99.99}'
```
- Delete:
```bash
curl -u admin:password123 -X DELETE http://127.0.0.1:8000/transactions/1 -i
```

## Run DSA Comparison
```bash
python dsa/dsa_compare.py
```
Outputs average timings and an observation. Ensure at least 20 records exist (script will add test records if needed).

## Screenshots to Include
Save to `screenshots/`:
- Successful GET with authentication
- Unauthorized request (missing/invalid credentials)
- Successful POST, PUT, DELETE

## Running the API

```bash
python API/server.py
```

Server runs on `http://127.0.0.1:8000`.

Auth credentials:
- Username: `admin`
- Password: `password123`

## Security Discussion (for report)
- Basic Auth is weak without TLS; credentials can be intercepted and are reused on every request.
- Prefer JWT or OAuth2 for stronger security, token rotation, and scoped access.

## Key Features
- Complete XML parsing to JSON with all required fields
- Full CRUD API endpoints (GET, POST, PUT, DELETE)
- Basic Authentication implementation with security analysis
- Comprehensive API documentation with examples and error codes
- DSA integration comparing linear search vs dictionary lookup with performance testing
- Database design with ERD and documentation

## Project Links
- System Architecture: [https://drive.google.com/file/d/1HsT7zy_rY5yrXu_hj6QoLXynkAvLYqsi/view?usp=sharing]
- ERD Diagram: [https://drive.google.com/file/d/1C4vF6A7KHkcdj6qKuPrMPtjd5aZPzCfP/view?ts=68cd1754]
- Scrum Board: [https://alustudent-team-pch2djpv.atlassian.net/jira/software/projects/SCRUM/boards/1?atlOrigin=eyJpIjoiNTdiNTU5YTJiNzEyNDJiYzk0MmQxOTQ3M2YwNzVjZWYiLCJwIjoiaiJ9]
