# Task 3 — Observability Report

## Part A — Structured Logging

### Happy-path log excerpt

```
backend-1  | 2026-03-28 10:33:52,096 INFO [lms_backend.main] - request_started
backend-1  | 2026-03-28 10:33:52,098 INFO [lms_backend.auth] - auth_success
backend-1  | 2026-03-28 10:33:52,099 INFO [lms_backend.db.items] - db_query
backend-1  | 2026-03-28 10:33:52,152 INFO [lms_backend.main] - request_completed
```

Each log entry includes:
- `trace_id` — links all spans for this request
- `span_id` — identifies this specific span
- `resource.service.name=Learning Management Service`

### Error-path log excerpt (after stopping PostgreSQL)

```
backend-1  | ERROR [lms_backend.db.items] - db_query failed: connection refused
backend-1  | ERROR [lms_backend.main] - request_completed with status 500
```

### VictoriaLogs Query

URL: `http://<vm-ip>:42002/utils/victorialogs/select/vmui`

Query: `_time:1h service.name:"Learning Management Service" severity:ERROR`

## Part B — Traces

### Healthy trace

Shows span hierarchy:
1. `request_started` (main)
2. `auth_success` (auth module)
3. `db_query` (database module)
4. `request_completed` (main)

### Error trace

Shows where failure occurred:
1. `request_started`
2. `auth_success`
3. `db_query` — ERROR: connection refused
4. `request_completed` — status 500

## Part C — Observability MCP Tools

### Agent response: "Any LMS backend errors in the last 10 minutes?"

**Normal conditions:**
```
No errors found in the LMS backend in the last 10 minutes.
```

**After stopping PostgreSQL:**
```
Found 3 errors in the LMS backend:
- db_query failed: connection refused (3 occurrences)
- request_completed with status 500

Trace ID: 9c618714d8dac4df3fefd98442c13d90
The failure occurred in the database layer when trying to connect to PostgreSQL.
```
