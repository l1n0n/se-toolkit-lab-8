# Lab 8 — Report

Paste your checkpoint evidence below. Add screenshots as image files in the repo and reference them with `![description](path)`.

## Task 1A — Bare agent

**Checkpoint 1:** "What is the agentic loop?"

```
The agentic loop is the fundamental cycle that autonomous AI agents follow to accomplish tasks. It's the core reasoning and action pattern that enables agents to work independently toward goals.

The Basic Loop:
 Perceive → Reason → Act → Observe → (repeat)

1. Perceive - The agent gathers information about its environment
2. Reason - The agent processes information and plans
3. Act - The agent executes its decision
4. Observe - The agent receives feedback

Then the loop repeats until the goal is achieved.
```

**Checkpoint 2:** "What labs are available in our LMS?"

Без MCP инструментов агент не имеет доступа к реальному бэкенду. Он исследует файлы репозитория и отвечает на основе документации:

```
Based on my exploration, here are the available labs in this LMS:

Required Labs (Lab 8 — The Agent is the Interface)
 1. Task 1: Set Up the Agent
 2. Task 2: Deploy and Connect a Web Client
 3. Task 3: Give the Agent New Eyes
 4. Task 4: Diagnose a Failure and Make the Agent Proactive
```

## Task 1B — Agent with LMS tools

**Checkpoint 1:** "What labs are available?"

С MCP инструментами агент возвращает **реальные данные** из бэкенда:

```
Here are the available labs:
 1. Lab 01 – Products, Architecture & Roles
 2. Lab 02 — Run, Fix, and Deploy a Backend Service
 3. Lab 03 — Backend API: Explore, Debug, Implement, Deploy
 4. Lab 04 — Testing, Front-end, and AI Agents
 5. Lab 05 — Data Pipeline and Analytics Dashboard
 6. Lab 06 — Build Your Own Agent
 7. Lab 07 — Build a Client with an AI Coding Agent
 8. lab-08
```

**Checkpoint 2:** "Is the LMS backend healthy?"

```
Yes, the LMS backend is healthy. It currently has 56 items in the system.
```

Агент использует MCP инструмент `lms_health` и возвращает реальный статус бэкенда.

## Task 1C — Skill prompt

**Checkpoint:** "Show me the scores" (без указания лабы)

С skill prompt агент следует правильной стратегии — сначала получает список лаб, затем просит выбрать:

```
I'll help you view the scores. First, let me check what labs are available in the LMS.
[Tool call: mcp_lms_lms_labs({})]

I can see there are 8 labs available. To show you the scores, I need to know which lab you're interested in. Let me present the options:

Available Labs:
 1. lab-01 — Lab 01 – Products, Architecture & Roles
 2. lab-02 — Lab 02 — Run, Fix, and Deploy a Backend Service
 ...
 8. lab-08 — lab-08

Which lab would you like to see the scores for?
```

## Task 2A — Deployed agent

Nanobot запущен как Docker сервис через `nanobot gateway`.

**Startup log excerpt:**

```
✓ Channels enabled: webchat
✓ Heartbeat: every 1800s
MCP server 'lms': connected, 9 tools registered
MCP server 'mcp_webchat': connected, 1 tools registered
Agent loop started
```

## Task 2B — Web client

Flutter web клиент доступен по адресу `http://<vm-ip>:42002/flutter/`.

**Тест WebSocket endpoint:**

```
$ echo '{"content":"What labs are available?"}' | websocat 'ws://localhost:42002/ws/chat?access_key=my-secret-nanobot-key'

{"type":"text","content":"Here are the available labs:
| Lab ID | Title |
|--------|-------|
| lab-01 | Lab 01 – Products, Architecture & Roles |
| lab-02 | Lab 02 — Run, Fix, and Deploy a Backend Service |
...
| lab-08 | lab-08 |"}
```

**Функциональность:**

- ✅ Login с `NANOBOT_ACCESS_KEY` работает
- ✅ Агент отвечает на общие вопросы
- ✅ Агент отвечает на LMS-вопросы с реальными данными
- ✅ При запросе "Show me the scores" без указания лабы — показывает structured UI choice
- ✅ MCP webchat сервер подключен и отправляет UI payloads

**Structured UI тест:**

```
Tool call: mcp_mcp_webchat_ui_message({
  "chat_id": "...",
  "payload": {
    "type": "choice",
    "text": "Which lab would you like to see scores for?",
    "choices": [...]
  }
})
```

## Task 3A — Structured logging

**Happy-path log excerpt:**

```
backend-1  | INFO [lms_backend.main] - request_started
backend-1  | INFO [lms_backend.auth] - auth_success
backend-1  | INFO [lms_backend.db.items] - db_query
backend-1  | INFO [lms_backend.main] - request_completed
```

Each log entry includes `trace_id`, `span_id`, and `service.name`.

**Error-path log excerpt (after stopping PostgreSQL):**

```
backend-1  | ERROR [lms_backend.db.items] - db_query failed: connection refused
backend-1  | ERROR [lms_backend.main] - request_completed with status 500
```

**VictoriaLogs Query:**
URL: `http://<vm-ip>:42002/utils/victorialogs/select/vmui`
Query: `_time:1h service.name:"Learning Management Service" severity:ERROR`

## Task 3B — Traces

**Healthy trace:** Shows span hierarchy: request_started → auth_success → db_query → request_completed

**Error trace:** Shows failure at db_query span with error message

## Task 3C — Observability MCP tools

**Created MCP server:** `mcp/mcp-obs/` with 4 tools:

- `logs_search` — Search VictoriaLogs using LogsQL
- `logs_error_count` — Count errors per service
- `traces_list` — List recent traces
- `traces_get` — Fetch trace by ID

**Agent response (normal conditions):**

```
Good news! There are **no errors** in the LMS backend in the last 10 minutes.
The system appears to be running smoothly.
```

**Agent response (after stopping PostgreSQL):**

```
Found errors in the LMS backend:
- db_query failed: connection refused
The failure occurred in the database layer when PostgreSQL was unreachable.
```

## Task 4A — Multi-step investigation

**Agent response to "What went wrong?" (PostgreSQL stopped):**

```
## What Went Wrong

**3 errors** occurred in the **Learning Management Service** in the last 10 minutes.

### Root Cause
The failure occurred in the database layer:
- **Service:** Learning Management Service
- **Operation:** db_query (SQLAlchemy)
- **Error:** "Name or service not known" - PostgreSQL connection failed
- **Trace ID:** dddfff25649611ed189c80fc8239fd8f

### Evidence from Logs
- `severity:ERROR` entries found with `event:db_query`
- SQLAlchemy connection error when trying to connect to PostgreSQL

### Evidence from Trace
- Trace shows request flow: request_started → auth_success → db_query (FAILED)
- The db_query span failed with socket.gaierror: [Errno -2] Name or service not known

### Summary
The LMS backend cannot connect to PostgreSQL database. All requests that require database access are failing.
```

**Investigation flow:**

1. `logs_error_count` → found 3 errors
2. `logs_search` → found error entries with trace_id
3. `traces_get` → fetched full trace showing failure at db_query span

## Task 4B — Proactive health check

**Created scheduled job:**

```
**Scheduled Jobs:**

| Job | ID | Interval | Next Run |
|-----|-----|----------|----------|
| LMS Health Check | 59ae1e1f | Every 2 minutes | 2026-03-28 11:16 UTC |
```

**Proactive health report (while PostgreSQL stopped):**

```
**LMS Health Check** (2026-03-28 11:14 UTC)

✅ **System looks healthy**

- Errors in last 2 minutes: 0
- Service: Learning Management Service
```

Note: The first report showed healthy because no new errors occurred in the 2-minute window. After triggering another request, the next report showed errors.

## Task 4C — Bug fix and recovery

### 1. Root Cause

**Planted bug location:** `backend/src/lms_backend/routers/items.py` lines 22-29

**Problem:** The exception handler in `get_items()` was catching all exceptions and returning HTTP 404 "Items not found" instead of properly signaling a database failure:

```python
# BEFORE (buggy):
except Exception as exc:
    logger.warning("items_list_failed_as_not_found", ...)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Items not found",
    ) from exc
```

This masked the real PostgreSQL connection error and misled users into thinking items were missing rather than the database being unavailable.

### 2. Fix

Changed the exception handler to return HTTP 500 with the actual error message:

```python
# AFTER (fixed):
except Exception as exc:
    logger.error(
        "items_list_failed",
        extra={"event": "items_list_failed", "error": str(exc)},
    )
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Database error: {str(exc)}",
    ) from exc
```

### 3. Post-fix failure check

After redeploy, with PostgreSQL stopped, the agent now reports the real error:

```
Found errors in the LMS backend:
- Database error: [Errno -2] Name or service not known
- The failure occurred when trying to connect to PostgreSQL
```

### 4. Healthy follow-up

After restarting PostgreSQL, the scheduled health check reports:

```
Good news! There are **0 errors** in the LMS backend over the last 2 minutes.
The system appears to be running smoothly.
```

## Task 4B — Proactive health check

<!-- Screenshot or transcript of the proactive health report that appears in the Flutter chat -->

## Task 4C — Bug fix and recovery

<!-- 1. Root cause identified
     2. Code fix (diff or description)
     3. Post-fix response to "What went wrong?" showing the real underlying failure
     4. Healthy follow-up report or transcript after recovery -->
