---
name: lms
description: Use LMS MCP tools for live course data
always: true
---

# LMS Skill

You have access to LMS backend data through MCP tools. Use them to answer questions about labs, learners, scores, and completion rates.

## Available Tools

- **lms_health** — Check if the LMS backend is healthy and get item count
- **lms_labs** — List all available labs
- **lms_learners** — List all registered learners
- **lms_pass_rates** — Get pass rates for a specific lab (requires lab parameter)
- **lms_timeline** — Get submission timeline for a specific lab (requires lab parameter)
- **lms_groups** — Get group performance for a specific lab (requires lab parameter)
- **lms_top_learners** — Get top learners for a specific lab (requires lab parameter)
- **lms_completion_rate** — Get completion rate (passed/total) for a specific lab
- **lms_sync_pipeline** — Trigger the LMS sync pipeline

## Strategy

### When user asks about scores, pass rates, completion, groups, timeline, or top learners WITHOUT naming a lab:

1. Call **lms_labs** first to get the list of available labs
2. If multiple labs exist, use the **structured-ui** skill to present a choice to the user
3. Use each lab's title as the label for the choice
4. Pass the lab identifier as the value

### When user asks about labs:

- Call **lms_labs** and present the results in a clear, formatted list
- Include both the lab identifier and title

### When user asks about backend health:

- Call **lms_health** and report the status and item count

### When user asks for completion rate or pass rate:

- If lab is specified, call the appropriate tool directly
- If lab is NOT specified, follow the strategy above (call lms_labs first, then ask for choice)

### Formatting numeric results:

- Present percentages with one decimal place (e.g., 89.1%)
- Show counts as integers
- Use tables for comparing multiple labs

### When the user asks "what can you do?":

Explain that you can:
- Check LMS backend health
- List available labs
- Get pass rates, completion rates, and timelines for specific labs
- Show top learners and group performance
- Trigger the sync pipeline

Mention that you need a lab identifier for detailed queries about scores or performance.

## Response Style

- Keep responses concise and focused on the data
- Use tables when comparing multiple labs or learners
- When a lab parameter is needed but not provided, ask the user to choose using structured UI
- Do not hallucinate data — always call the appropriate MCP tool first
