# Security

## Authentication and sessions

- Unauthenticated sessions see only the sign-in form.
- App execution stops before navigation and database reads until authentication.
- Each Streamlit session owns its Supabase client and authenticated token state.
- Every service mutation calls `require_authenticated_user`.
- Logout calls Supabase sign-out, clears all session state, and clears data caches.

## Authorization and RLS

The generated migration revokes anonymous table access, grants only required
operations to `authenticated`, enables RLS, and creates select/insert/update
policies used by the dashboard. Candidate and job update policies are required
for the production management features. Delete privileges and policies are not
granted.

The current schema has no recruiter profile, organization, or role table.
Therefore any Supabase-authenticated user is treated as a recruiter. Before
production, disable public sign-up or restrict access to approved invitations.

Phase 2 introduces ADMIN, RECRUITER, and VIEWER checks in UI and service code.
Before the v1.1 migration exists, authenticated v1.0 users retain RECRUITER
behavior for backward compatibility. After migration, existing users are
backfilled as RECRUITER, new/unprovisioned users resolve to VIEWER, and role-aware
RLS blocks VIEWER writes. ADMIN-only role management is defined by policy but no
admin UI is enabled before migration approval.

## Communication safety

Messages require a visible preview and explicit confirmation. Webhooks must be
HTTPS except for localhost development, embedded URL credentials are rejected,
requests time out, retries are bounded, and audit recipients are masked.

## AI safety

AI Recruiter operations are read-only and allowlisted. User input is never
interpolated into SQL. Database mutation terms and prompt-override patterns are
blocked, and displayed answers are based only on stored data.

Interview Copilot output is recruiter assistance, not a hiring decision. It
does not infer protected characteristics, change stages, or persist interview
responses. Semantic-search fallback uses only real stored candidate text.

Private AI conversations/bookmarks are owner-scoped by the proposed RLS. The
session fallback is isolated per Streamlit session and is not durable.

## Migration procedure

`supabase/migrations/20260720_authenticated_recruiter_rls.sql` is review-only.
Inspect existing policies first: PostgreSQL permissive policies are additive, so
an old anonymous/testing policy can still broaden access. Apply changes only
through the approved database release process, then run the verification query
included in the migration.

Review `20260807_phase2_v1_1_proposal.sql` after the base migration. It enables
pgvector, adds Phase 2 tables, and replaces broad write policies with role-aware
policies. Neither migration has been applied by this project workflow.

## Known production consideration

Communication audit history currently uses a local JSON-lines log. In stateless
or horizontally scaled hosting, route these events to a durable centralized
store before relying on the page as the system of record.
