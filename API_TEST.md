# API Testing Guide

Manual API testing reference (Postman / Thunder Client).  
All requests below were executed against a live server on **2026-06-21**.

**Base URL:** `http://127.0.0.1:8000`  
**Important:** All URLs must end with `/`  
**Money:** `amount_minor` = paisa/cents (`10000` = 100.00 BDT)

---

## Setup before testing

```powershell
docker compose -f docker-compose.infra.yml up -d
.\venv\Scripts\python.exe manage.py runserver
```

### Postman auth (recommended)

| Field | Value |
|-------|-------|
| Auth Type | API Key |
| Key | `Api-Key` |
| Value | your `api_key` from Test 1 |
| Add to | Header |

---

## Test 1 — Create tenant

**POST** `http://127.0.0.1:8000/api/v1/tenants/`

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "name": "Postman Demo Corp"
}
```

**Response `201`:**
```json
{
  "id": 7,
  "name": "Postman Demo Corp",
  "api_key": "jvK_xRS_Cwq8HgIppcU6xvnwYmnR6X2NwbcLHjkyrZg"
}
```

Save `api_key` for all protected endpoints below.

---

## Test 2 — Create wallet #1

**POST** `http://127.0.0.1:8000/api/v1/wallets/`

**Headers:**
```
Content-Type: application/json
Api-Key: jvK_xRS_Cwq8HgIppcU6xvnwYmnR6X2NwbcLHjkyrZg
```

**Body:**
```json
{
  "user_ref": "user-001",
  "currency": "BDT"
}
```

**Response `201`:**
```json
{
  "id": 5,
  "user_ref": "user-001",
  "currency": "BDT",
  "balance_minor": 0,
  "created_at": "2026-06-21T20:38:45.902676+00:00"
}
```

---

## Test 3 — Create wallet #2

**POST** `http://127.0.0.1:8000/api/v1/wallets/`

**Body:**
```json
{
  "user_ref": "user-002",
  "currency": "BDT"
}
```

**Response `201`:**
```json
{
  "id": 6,
  "user_ref": "user-002",
  "currency": "BDT",
  "balance_minor": 0,
  "created_at": "2026-06-21T20:38:45.941949+00:00"
}
```

---

## Test 4 — Deposit

**POST** `http://127.0.0.1:8000/api/v1/wallets/5/deposit/`

**Headers:**
```
Content-Type: application/json
Api-Key: jvK_xRS_Cwq8HgIppcU6xvnwYmnR6X2NwbcLHjkyrZg
Idempotency-Key: dep-001
```

**Body:**
```json
{
  "amount_minor": 10000,
  "reference": "top-up"
}
```

**Response `201`:**
```json
{
  "transaction_id": 12,
  "wallet_id": 5,
  "type": "DEPOSIT",
  "amount_minor": 10000,
  "balance_minor": 10000
}
```

---

## Test 5 — Get wallet balance

**GET** `http://127.0.0.1:8000/api/v1/wallets/5/`

**Headers:**
```
Api-Key: jvK_xRS_Cwq8HgIppcU6xvnwYmnR6X2NwbcLHjkyrZg
```

**Response `200`:**
```json
{
  "id": 5,
  "user_ref": "user-001",
  "currency": "BDT",
  "balance_minor": 10000,
  "created_at": "2026-06-21T20:38:45.902676+00:00"
}
```

---

## Test 6 — Transaction history (paginated)

**GET** `http://127.0.0.1:8000/api/v1/wallets/5/transactions/`

**Headers:**
```
Api-Key: jvK_xRS_Cwq8HgIppcU6xvnwYmnR6X2NwbcLHjkyrZg
```

**Response `200`:**
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 12,
      "type": "DEPOSIT",
      "amount_minor": 10000,
      "reference": "top-up",
      "idempotency_key": "dep-001",
      "transfer_group_id": null,
      "created_at": "2026-06-21T20:38:45.993689Z"
    }
  ]
}
```

---

## Test 7 — Withdraw (success)

**POST** `http://127.0.0.1:8000/api/v1/wallets/5/withdraw/`

**Headers:**
```
Content-Type: application/json
Api-Key: jvK_xRS_Cwq8HgIppcU6xvnwYmnR6X2NwbcLHjkyrZg
Idempotency-Key: wd-001
```

**Body:**
```json
{
  "amount_minor": 3000
}
```

**Response `201`:**
```json
{
  "transaction_id": 13,
  "wallet_id": 5,
  "type": "WITHDRAW",
  "amount_minor": 3000,
  "balance_minor": 7000
}
```

---

## Test 8 — Withdraw (insufficient funds)

**POST** `http://127.0.0.1:8000/api/v1/wallets/5/withdraw/`

**Headers:**
```
Content-Type: application/json
Api-Key: jvK_xRS_Cwq8HgIppcU6xvnwYmnR6X2NwbcLHjkyrZg
Idempotency-Key: wd-fail
```

**Body:**
```json
{
  "amount_minor": 999999
}
```

**Response `400`:**
```json
{
  "error": "Insufficient funds"
}
```

---

## Test 9 — Transfer (success)

**POST** `http://127.0.0.1:8000/api/v1/transfers/`

**Headers:**
```
Content-Type: application/json
Api-Key: jvK_xRS_Cwq8HgIppcU6xvnwYmnR6X2NwbcLHjkyrZg
Idempotency-Key: xfer-001
```

**Body:**
```json
{
  "from_wallet_id": 5,
  "to_wallet_id": 6,
  "amount_minor": 2000,
  "reference": "pay user-002"
}
```

**Response `201`:**
```json
{
  "transfer_group_id": "41ce1da7-4d37-4c32-b0f4-a881d02e8fc9",
  "from_wallet_id": 5,
  "to_wallet_id": 6,
  "amount_minor": 2000,
  "from_balance_minor": 5000,
  "to_balance_minor": 2000,
  "transactions": [
    { "id": 14, "type": "TRANSFER_OUT" },
    { "id": 15, "type": "TRANSFER_IN" }
  ]
}
```

---

## Test 10 — Idempotency: first deposit

**POST** `http://127.0.0.1:8000/api/v1/wallets/5/deposit/`

**Headers:**
```
Idempotency-Key: dep-dup
```

**Body:**
```json
{
  "amount_minor": 5000,
  "reference": "dup"
}
```

**Response `201`:**
```json
{
  "transaction_id": 16,
  "wallet_id": 5,
  "type": "DEPOSIT",
  "amount_minor": 5000,
  "balance_minor": 10000
}
```

---

## Test 11 — Idempotency: retry (same key + same body)

Repeat **exact same request** as Test 10.

**Response `201` (same as Test 10 — no double charge):**
```json
{
  "transaction_id": 16,
  "wallet_id": 5,
  "type": "DEPOSIT",
  "amount_minor": 5000,
  "balance_minor": 10000
}
```

Note: `transaction_id` is identical. Balance did not increase again.

---

## Test 12 — Idempotency conflict (same key, different body)

**Request A** — **POST** deposit with `Idempotency-Key: dep-conflict`

**Body:**
```json
{ "amount_minor": 1000 }
```

**Response `201`:**
```json
{
  "transaction_id": 17,
  "wallet_id": 5,
  "type": "DEPOSIT",
  "amount_minor": 1000,
  "balance_minor": 11000
}
```

**Request B** — same key, different amount:

**Body:**
```json
{ "amount_minor": 9000 }
```

**Response `409`:**
```json
{
  "error": "Idempotency key reused with different request body"
}
```

---

## Test 13 — Cross-tenant access blocked

Create another tenant:

**POST** `http://127.0.0.1:8000/api/v1/tenants/`

**Body:**
```json
{ "name": "Other Corp" }
```

**Response `201`:**
```json
{
  "id": 8,
  "name": "Other Corp",
  "api_key": "3dbp5K8fBf7-8bF6Y2IiGcYvLb-xuX3AVGI3X8s6jzM"
}
```

Try to read wallet 5 with **Other Corp** key:

**GET** `http://127.0.0.1:8000/api/v1/wallets/5/`

**Headers:**
```
Api-Key: 3dbp5K8fBf7-8bF6Y2IiGcYvLb-xuX3AVGI3X8s6jzM
```

**Response `404`:**
```json
{
  "error": "Wallet not found"
}
```

---

## Test 14 — Missing API key

**GET** `http://127.0.0.1:8000/api/v1/wallets/5/`

No `Api-Key` header.

**Response `403`:**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

---

## Test 15 — Missing idempotency key

**POST** `http://127.0.0.1:8000/api/v1/wallets/5/deposit/`

No `Idempotency-Key` header.

**Body:**
```json
{ "amount_minor": 1000 }
```

**Response `409`:**
```json
{
  "error": "idempotency_key is required (header Idempotency-Key or body field)"
}
```

---

## Test 16 — Transfer to same wallet

**POST** `http://127.0.0.1:8000/api/v1/transfers/`

**Headers:**
```
Idempotency-Key: xfer-same
```

**Body:**
```json
{
  "from_wallet_id": 5,
  "to_wallet_id": 5,
  "amount_minor": 100
}
```

**Response `400`:**
```json
{
  "error": "Cannot transfer to the same wallet"
}
```
