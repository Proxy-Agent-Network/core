# Proxy Agent Network: API Specification (v1.0)

This document defines the RESTful endpoints for the Proxy Agent Registry. All requests and responses use `application/json`.

## Base URL
`http://localhost:5000/` (Development)

---

## Node & Task Endpoints

### 1. Post a New Task
**Endpoint:** `POST /api/v1/tasks/post`  
**Description:** Agents use this to submit a new task into the "Open" ledger.

**Request Body:**
```json
{
  "agent_id": "AGENT-007",
  "type": "NOTARY_VERIFY",
  "bid_sats": 75000
}
```

**Response:** `201 Created`
```json
{
  "status": "posted",
  "task_id": "TASK-ABCD123"
}
```

---

### 2. Complete a Task
**Endpoint:** `POST /api/v1/tasks/complete`  
**Description:** Notifies the registry that a task has been fulfilled. Triggers XP gain and Satoshi rewards.

**Request Body:**
```json
{
  "task_id": "TASK-ABCD123",
  "node_id": "NODE-XYZ999"
}
```

**Response:** `200 OK`
```json
{
  "status": "Success",
  "xp_gained": 7500
}
```

---

### 3. Node Heartbeat (Pulse)
**Endpoint:** `POST /api/v1/node/heartbeat`  
**Description:** Keeps the node status as "ONLINE" in the Mission Control UI.

**Request Body:**
```json
{
  "node_id": "NODE-XYZ999"
}
```

---

## Debug & Monitoring (GET)

### 1. View Node Status
**Endpoint:** `GET /debug/node_status`  

### 2. View Task Ledger
**Endpoint:** `GET /debug/view_tasks`  

---

## Security Note
In the current Genesis phase (v1.0), these endpoints are unauthenticated for local development. Signature verification is scheduled for Q2 2026.
