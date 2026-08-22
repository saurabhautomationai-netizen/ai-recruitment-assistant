# Features

## Candidate management

Recruiters can search and filter the candidate directory, inspect the existing
profile, edit core contact and experience fields, archive a candidate, and
restore an archived candidate. Archive uses `status = 'Archived'`; permanent
deletion is not available.

## Application management

Candidate applications can move through pending review, shortlisted, interview,
selected, and rejected stages. Recruiter notes are append-only through the UI.

## Job management

The Jobs page supports search, profile editing, close, reopen, archive, and
restore-by-reopen. Lifecycle values are stored in the existing `jobs.status`
field. No delete workflow exists.

## Interview management

Recruiters can schedule interviews and later change the date/time, interviewer,
or meeting link/location. Interviews can be marked scheduled, completed, or
cancelled. Schedule and status changes append snapshots to
`feedback._history`; feedback and ratings remain editable.

## Communication history

Confirmed email and WhatsApp sends use a bounded retry policy. Structured audit
events record channel, delivery status, attempts, timestamp, recruiter, masked
recipient, message type, application, and HTTP status. The page resolves the
related candidate and job from application data.

## AI Recruiter

The assistant supports allowlisted searches for skills, experience, ATS scores,
application stages, interview state, candidate comparisons, stored decision
rationale, and job matching. The UI includes suggested prompts, recent searches,
session conversation saves, JSON export, and candidate bookmarks.

## Analytics and UI

The overview and analytics pages provide recruitment metrics, pipeline views,
job distribution, and score summaries. Consistent wide tables, bordered cards,
loading indicators, filters, and empty states are used throughout the dashboard.

## Phase 2 / v1.1

### AI Interview Copilot — implemented with session storage

Builds a preparation brief from existing candidate, application, job, notes,
question, and feedback data. Recruiters can capture job-relevant responses,
track Technical, Experience, Behavioural, and Role Fit coverage, request neutral
follow-ups, and summarize evidence. It never changes candidate status or makes
an automated hiring decision. Transcript persistence is intentionally disabled.

### Resume semantic search — partially implemented

Natural-language and job-description searches are available through a clearly
labelled local cosine term-relevance fallback. True embedding similarity is
pending the pgvector migration and an approved embedding provider. No fake
candidate content is embedded.

### Bulk import/export — implemented

CSV and XLSX uploads are mapped only to supported existing candidate fields,
previewed, checked for required values and duplicate emails, and split into
valid/invalid rows before explicit confirmation. Filtered CSV/XLSX exports
support status, job, location, experience, and candidate-score filters.

### Calendar integration — credential pending

Google and Outlook event previews use real interview context and require
confirmation. External event creation remains stopped at the OAuth/provider
adapter boundary, so no calendar events are created by the current build.

### RBAC — application layer implemented; database migration pending

ADMIN and RECRUITER retain recruitment write features. VIEWER sees read-only
navigation and cannot use mutation services. Database-enforced roles and RLS
depend on the review-only v1.1 migration.

### Persistent AI and durable communications — adapters implemented

Conversations and candidate/job bookmarks prefer user-owned Supabase tables and
fall back to session state while the migration is pending. Communication logs
prefer Supabase and preserve the existing JSON-lines audit fallback.
