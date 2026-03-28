---
name: observability
description: Use observability MCP tools to investigate errors and system health
always: true
---

# Observability Skill

You have access to observability tools for querying VictoriaLogs and VictoriaTraces. Use them to investigate errors, understand system behavior, and diagnose failures.

## Available Tools

- **logs_search** — Search VictoriaLogs using LogsQL query
- **logs_error_count** — Count errors for a service over a time window
- **traces_list** — List recent traces for a service
- **traces_get** — Fetch a specific trace by ID

## Strategy

### When the user asks "What went wrong?" or "Check system health":

1. Start with **logs_error_count** for the LMS backend with time_range="10m"
2. If count > 0, use **logs_search** with query="severity:ERROR" and time_range="10m"
3. Look for `trace_id` in the log entries
4. If you find a trace_id, use **traces_get** to fetch the full trace
5. Summarize findings concisely — explain:
   - What service failed
   - What operation failed (e.g., "db_query", "SQLAlchemy error")
   - The error message
   - Evidence from both logs AND traces

### When the user asks about errors in a time window:

1. Call **logs_error_count** for that service and time window
2. If errors exist, call **logs_search** to inspect entries
3. Extract trace_id if available
4. Call **traces_get** for full context
5. Summarize: service + operation + error message

### Query patterns:

- For LMS backend errors: `service.name:"Learning Management Service" severity:ERROR`
- For time range: `_time:10m` for last 10 minutes, `_time:2m` for last 2 minutes
- For specific events: `event:db_query` or `event:request_completed`

### Response style:

- Keep responses concise and focused on the issue
- Don't dump raw JSON — summarize the findings
- Include trace_id when relevant for debugging
- Explain the failure point clearly (e.g., "PostgreSQL connection failed", "SQLAlchemy error in db_query")
- Cite both log evidence AND trace evidence in your answer

### Example workflow for "What went wrong?":

User: "What went wrong?"

1. Call `logs_error_count(service="Learning Management Service", time_range="10m")`
2. If count > 0, call `logs_search(query="severity:ERROR", limit=10, time_range="10m")`
3. Find entry with trace_id, e.g., "trace_id=abc123"
4. Call `traces_get(trace_id="abc123")` to see full failure context
5. Summarize: "Found 3 errors in the LMS backend. The failure occurred in db_query when PostgreSQL connection was refused. Trace abc123 shows the request failed at the database layer with SQLAlchemy error 'connection refused'. The backend returned 500 status."
