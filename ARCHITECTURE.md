# Architecture

## Runtime

`app.py` is the Streamlit entry point. It establishes the authentication
boundary, renders navigation, loads Supabase data, and dispatches page content.
Reusable presentation code lives in `components/`; authenticated data and
integration operations live in `services/`.

## Data flow

```text
Browser session
  → Streamlit authentication boundary
  → session-isolated Supabase client
  → PostgreSQL tables protected by RLS

Confirmed message
  → communication service validation
  → HTTPS webhook with bounded retry
  → structured local audit log

AI question
  → allowlisted intent parser
  → in-memory dataframe filtering/join
  → structured response renderer
```

## State and caching

Supabase table reads use `st.cache_data` with a 60-second TTL. Successful writes
clear the relevant cache before rerunning. Authentication clients and all UI
state are session-local. AI saves/bookmarks and recent communication confirmations
are session-scoped; the communication audit file is process-host persistent.

## External integrations

- Supabase Auth and PostgREST
- HTTPS n8n or compatible communication webhook
- Streamlit frontend

The app does not run migrations, deploy, or perform permanent deletes.

## Phase 2 boundaries

The Interview Copilot is deterministic and evidence-grounded; it does not call
an external model or persist recruiter-entered responses. Candidate relevance
search uses local cosine term scoring until pgvector and an embedding provider
are approved. `ai_persistence_service.py` and `communication_service.py` use
database-first adapters that catch missing-table errors and fall back to session
or local JSON-lines storage.

Calendar integration is split into provider-neutral event construction,
configuration detection, explicit confirmation, and a deliberately unimplemented
provider adapter. This prevents accidental events even if environment variables
are present.

Role checks exist in both UI and mutation services. The database becomes the
final authority only after `20260807_phase2_v1_1_proposal.sql` is reviewed and
applied manually.
