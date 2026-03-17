# Skill: search-db (read-only DB queries)

## What this skill does

This skill explains how the agent can run **read-only SQL queries** against the project’s Postgres database to inspect and analyze existing data, without modifying it.

It uses the script `agent_utils/search_db.py`, which:

- Connects to the Postgres DB using environment variables in `.env`:
  - `DB_NAME`, `DB_USER`, `DB_PASS`, `DB_HOST`, `DB_PORT`
- Opens a **read-only** session (`conn.set_session(readonly=True)`)
- Executes a user‑provided SQL `SELECT` query
- Prints results either as CSV or as a simple table to stdout

This is intended for **inspection, debugging, and analysis**, not for data mutation.

---

## When the agent should use this

The agent should suggest or use this capability whenever it needs to:

- **Understand the current state of the database**, e.g.:
  - “What cities are in the `ui_city` table?”
  - “How many rows are in `bookings` for the last 7 days?”
- **Inspect raw data** behind a bug, anomaly, or test case
- **Verify assumptions** about schema content (but not schema structure itself)
- **Explore distributions and aggregates** of existing data:
  - Counts, groupings, simple statistics (e.g., via `COUNT`, `AVG`, `GROUP BY`)

The agent should *not* use this for any query that is meant to change data or schema.

---

## How to run it (for the user / agent to instruct)

From the project root:

```bash
uv run agent_utils/search_db.py --query "<YOUR_SELECT_QUERY>" --format csv