-- Production RLS migration for the AI Recruitment Dashboard.
--
-- IMPORTANT:
-- 1. Apply only after review through the approved Supabase release process.
-- 2. This migration affects only the five recruitment tables named below.
-- 3. A "recruiter" is any user authenticated through Supabase Auth.
--    This migration intentionally does not depend on recruiter_profiles.
-- 4. Deletes remain intentionally denied: no DELETE privilege or policy is
--    granted for any recruitment table.

begin;

-- =========================================================
-- Remove old development/testing policies
-- =========================================================

drop policy if exists "Dashboard can read applications"
on public.applications;

drop policy if exists "Dashboard can read candidates"
on public.candidates;

drop policy if exists "Allow dashboard to insert interviews"
on public.interviews;

drop policy if exists "Allow dashboard to read interviews"
on public.interviews;

drop policy if exists "Allow dashboard to update interviews"
on public.interviews;

drop policy if exists "Dashboard can read jobs"
on public.jobs;

drop policy if exists "Allow dashboard to insert recruiter notes"
on public.recruiter_notes;

drop policy if exists "Allow dashboard to read recruiter notes"
on public.recruiter_notes;

drop policy if exists "Allow dashboard to update recruiter notes"
on public.recruiter_notes;


-- =========================================================
-- Harden table privileges
-- =========================================================

-- Remove anonymous/direct PUBLIC access.

revoke all on table public.candidates from anon;
revoke all on table public.candidates from public;

revoke all on table public.applications from anon;
revoke all on table public.applications from public;

revoke all on table public.jobs from anon;
revoke all on table public.jobs from public;

revoke all on table public.interviews from anon;
revoke all on table public.interviews from public;

revoke all on table public.recruiter_notes from anon;
revoke all on table public.recruiter_notes from public;


-- Remove the existing overly broad authenticated grants.

revoke all on table public.candidates from authenticated;
revoke all on table public.applications from authenticated;
revoke all on table public.jobs from authenticated;
revoke all on table public.interviews from authenticated;
revoke all on table public.recruiter_notes from authenticated;


-- =========================================================
-- Grant authenticated users only required operations
-- =========================================================

grant usage on schema public to authenticated;

grant select, update
on table public.candidates
to authenticated;

grant select, update
on table public.applications
to authenticated;

grant select, update
on table public.jobs
to authenticated;

grant select, insert, update
on table public.interviews
to authenticated;

grant select, insert
on table public.recruiter_notes
to authenticated;


-- =========================================================
-- Enable RLS
-- =========================================================

alter table public.candidates enable row level security;
alter table public.applications enable row level security;
alter table public.jobs enable row level security;
alter table public.interviews enable row level security;
alter table public.recruiter_notes enable row level security;


-- =========================================================
-- Candidates
-- =========================================================

drop policy if exists authenticated_recruiters_select_candidates
on public.candidates;

create policy authenticated_recruiters_select_candidates
on public.candidates
for select
to authenticated
using (true);


drop policy if exists authenticated_recruiters_update_candidates
on public.candidates;

create policy authenticated_recruiters_update_candidates
on public.candidates
for update
to authenticated
using (true)
with check (true);


-- =========================================================
-- Applications
-- =========================================================

drop policy if exists authenticated_recruiters_select_applications
on public.applications;

create policy authenticated_recruiters_select_applications
on public.applications
for select
to authenticated
using (true);


drop policy if exists authenticated_recruiters_update_applications
on public.applications;

create policy authenticated_recruiters_update_applications
on public.applications
for update
to authenticated
using (true)
with check (true);


-- =========================================================
-- Jobs
-- =========================================================

drop policy if exists authenticated_recruiters_select_jobs
on public.jobs;

create policy authenticated_recruiters_select_jobs
on public.jobs
for select
to authenticated
using (true);


drop policy if exists authenticated_recruiters_update_jobs
on public.jobs;

create policy authenticated_recruiters_update_jobs
on public.jobs
for update
to authenticated
using (true)
with check (true);


-- =========================================================
-- Interviews
-- =========================================================

drop policy if exists authenticated_recruiters_select_interviews
on public.interviews;

create policy authenticated_recruiters_select_interviews
on public.interviews
for select
to authenticated
using (true);


drop policy if exists authenticated_recruiters_insert_interviews
on public.interviews;

create policy authenticated_recruiters_insert_interviews
on public.interviews
for insert
to authenticated
with check (true);


drop policy if exists authenticated_recruiters_update_interviews
on public.interviews;

create policy authenticated_recruiters_update_interviews
on public.interviews
for update
to authenticated
using (true)
with check (true);


-- =========================================================
-- Recruiter Notes
-- Append-only by design
-- =========================================================

drop policy if exists authenticated_recruiters_select_recruiter_notes
on public.recruiter_notes;

create policy authenticated_recruiters_select_recruiter_notes
on public.recruiter_notes
for select
to authenticated
using (true);


drop policy if exists authenticated_recruiters_insert_recruiter_notes
on public.recruiter_notes;

create policy authenticated_recruiters_insert_recruiter_notes
on public.recruiter_notes
for insert
to authenticated
with check (true);


commit;