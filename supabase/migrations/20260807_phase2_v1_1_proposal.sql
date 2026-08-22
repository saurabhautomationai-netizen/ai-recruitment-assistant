-- AI Recruitment Assistant v1.1 schema and authorization proposal.
-- REVIEW ONLY. Do not apply automatically.
-- This migration depends on the existing candidates/jobs/applications schema.

begin;

create extension if not exists vector;

create table if not exists public.recruiter_profiles (
    user_id uuid primary key references auth.users(id) on delete cascade,
    role text not null default 'VIEWER'
        check (role in ('ADMIN', 'RECRUITER', 'VIEWER')),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

-- Preserve access for users who already existed before role support. Every
-- existing Auth user becomes a RECRUITER; no ADMIN is created automatically.
-- After this migration, the first ADMIN must be promoted manually through a
-- privileged Supabase SQL operation. This intentionally avoids hard-coding a
-- production user UUID. New users should be provisioned explicitly and default
-- to VIEWER.
insert into public.recruiter_profiles (user_id, role)
select id, 'RECRUITER' from auth.users
on conflict (user_id) do nothing;

create or replace function public.current_recruiter_role()
returns text
language sql
stable
security definer
set search_path = pg_catalog, public
as $$
    select coalesce(
        (select role from public.recruiter_profiles where user_id = auth.uid()),
        'VIEWER'
    );
$$;

revoke all on function public.current_recruiter_role() from public;
grant execute on function public.current_recruiter_role() to authenticated;

create table if not exists public.candidate_embeddings (
    candidate_id uuid primary key references public.candidates(id) on delete cascade,
    content text not null,
    content_hash text not null,
    embedding vector not null,
    provider text not null,
    model text not null,
    updated_at timestamptz not null default now()
);

-- This table may remain empty until the production embedding provider is
-- configured. Before generating embeddings, select one approved provider,
-- model, and vector dimension for the deployment. Do not insert or compare
-- mixed incompatible dimensions. Add a vector similarity index only after that
-- production embedding strategy and its dimension are fixed.

create or replace function public.match_candidate_embeddings(
    query_embedding vector,
    match_count integer default 20,
    minimum_similarity double precision default 0
)
returns table (candidate_id uuid, similarity double precision)
language sql
stable
security invoker
set search_path = pg_catalog, public, extensions
as $$
    with compatible_embeddings as materialized (
        select ce.candidate_id, ce.embedding
        from public.candidate_embeddings ce
        where vector_dims(ce.embedding) = vector_dims(query_embedding)
    )
    select ce.candidate_id,
           1 - (ce.embedding <=> query_embedding) as similarity
    from compatible_embeddings ce
    where 1 - (ce.embedding <=> query_embedding) >=
          greatest(-1.0, least(coalesce(minimum_similarity, 0), 1.0))
    order by ce.embedding <=> query_embedding
    limit greatest(1, least(coalesce(match_count, 20), 100));
$$;

revoke all on function public.match_candidate_embeddings(
    vector, integer, double precision
) from public;
revoke all on function public.match_candidate_embeddings(
    vector, integer, double precision
) from anon;

create table if not exists public.ai_conversations (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users(id) on delete cascade,
    title text not null check (char_length(title) between 1 and 120),
    messages jsonb not null default '[]'::jsonb,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

alter table public.ai_conversations
    drop constraint if exists ai_conversations_messages_array;
alter table public.ai_conversations
    add constraint ai_conversations_messages_array
    check (jsonb_typeof(messages) = 'array');

create table if not exists public.candidate_bookmarks (
    user_id uuid not null references auth.users(id) on delete cascade,
    candidate_id uuid not null references public.candidates(id) on delete cascade,
    created_at timestamptz not null default now(),
    primary key (user_id, candidate_id)
);

create table if not exists public.job_bookmarks (
    user_id uuid not null references auth.users(id) on delete cascade,
    job_id uuid not null references public.jobs(id) on delete cascade,
    created_at timestamptz not null default now(),
    primary key (user_id, job_id)
);

create table if not exists public.communication_logs (
    id uuid primary key default gen_random_uuid(),
    candidate_id uuid references public.candidates(id) on delete set null,
    application_id uuid references public.applications(id) on delete set null,
    job_id uuid references public.jobs(id) on delete set null,
    user_id uuid not null references auth.users(id) on delete restrict,
    channel text not null check (channel in ('email', 'whatsapp')),
    template text not null,
    destination text not null,
    status text not null check (status in ('success', 'failed', 'pending')),
    retry_count integer not null default 0 check (retry_count >= 0),
    provider_result jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now()
);

alter table public.recruiter_profiles enable row level security;
alter table public.candidate_embeddings enable row level security;
alter table public.ai_conversations enable row level security;
alter table public.candidate_bookmarks enable row level security;
alter table public.job_bookmarks enable row level security;
alter table public.communication_logs enable row level security;

-- Remove broad v1.0 write policies before introducing role-aware replacements.
drop policy if exists authenticated_recruiters_update_candidates on public.candidates;
drop policy if exists authenticated_recruiters_update_applications on public.applications;
drop policy if exists authenticated_recruiters_update_jobs on public.jobs;
drop policy if exists authenticated_recruiters_insert_interviews on public.interviews;
drop policy if exists authenticated_recruiters_update_interviews on public.interviews;
drop policy if exists authenticated_recruiters_insert_recruiter_notes on public.recruiter_notes;

drop policy if exists role_writers_insert_candidates on public.candidates;
create policy role_writers_insert_candidates on public.candidates for insert
to authenticated with check (public.current_recruiter_role() in ('ADMIN','RECRUITER'));
drop policy if exists role_writers_update_candidates on public.candidates;
create policy role_writers_update_candidates on public.candidates for update
to authenticated using (public.current_recruiter_role() in ('ADMIN','RECRUITER'))
with check (public.current_recruiter_role() in ('ADMIN','RECRUITER'));
drop policy if exists role_writers_update_applications on public.applications;
create policy role_writers_update_applications on public.applications for update
to authenticated using (public.current_recruiter_role() in ('ADMIN','RECRUITER'))
with check (public.current_recruiter_role() in ('ADMIN','RECRUITER'));
drop policy if exists role_writers_update_jobs on public.jobs;
create policy role_writers_update_jobs on public.jobs for update
to authenticated using (public.current_recruiter_role() in ('ADMIN','RECRUITER'))
with check (public.current_recruiter_role() in ('ADMIN','RECRUITER'));
drop policy if exists role_writers_insert_interviews on public.interviews;
create policy role_writers_insert_interviews on public.interviews for insert
to authenticated with check (public.current_recruiter_role() in ('ADMIN','RECRUITER'));
drop policy if exists role_writers_update_interviews on public.interviews;
create policy role_writers_update_interviews on public.interviews for update
to authenticated using (public.current_recruiter_role() in ('ADMIN','RECRUITER'))
with check (public.current_recruiter_role() in ('ADMIN','RECRUITER'));
drop policy if exists role_writers_insert_notes on public.recruiter_notes;
create policy role_writers_insert_notes on public.recruiter_notes for insert
to authenticated with check (public.current_recruiter_role() in ('ADMIN','RECRUITER'));

drop policy if exists users_read_own_profile on public.recruiter_profiles;
create policy users_read_own_profile on public.recruiter_profiles for select
to authenticated using (user_id = auth.uid() or public.current_recruiter_role() = 'ADMIN');
drop policy if exists admins_manage_profiles on public.recruiter_profiles;
create policy admins_manage_profiles on public.recruiter_profiles for all
to authenticated using (public.current_recruiter_role() = 'ADMIN')
with check (public.current_recruiter_role() = 'ADMIN');

drop policy if exists authenticated_read_embeddings on public.candidate_embeddings;
create policy authenticated_read_embeddings on public.candidate_embeddings for select
to authenticated using (true);
drop policy if exists role_writers_manage_embeddings on public.candidate_embeddings;
create policy role_writers_manage_embeddings on public.candidate_embeddings for all
to authenticated using (public.current_recruiter_role() in ('ADMIN','RECRUITER'))
with check (public.current_recruiter_role() in ('ADMIN','RECRUITER'));

drop policy if exists users_manage_own_conversations on public.ai_conversations;
create policy users_manage_own_conversations on public.ai_conversations for all
to authenticated using (user_id = auth.uid()) with check (user_id = auth.uid());
drop policy if exists users_manage_own_candidate_bookmarks on public.candidate_bookmarks;
create policy users_manage_own_candidate_bookmarks on public.candidate_bookmarks for all
to authenticated using (user_id = auth.uid()) with check (user_id = auth.uid());
drop policy if exists users_manage_own_job_bookmarks on public.job_bookmarks;
create policy users_manage_own_job_bookmarks on public.job_bookmarks for all
to authenticated using (user_id = auth.uid()) with check (user_id = auth.uid());
drop policy if exists recruiters_read_communication_logs on public.communication_logs;
create policy recruiters_read_communication_logs on public.communication_logs for select
to authenticated using (public.current_recruiter_role() in ('ADMIN','RECRUITER'));
drop policy if exists recruiters_insert_communication_logs on public.communication_logs;
create policy recruiters_insert_communication_logs on public.communication_logs for insert
to authenticated with check (
    user_id = auth.uid() and public.current_recruiter_role() in ('ADMIN','RECRUITER')
);

grant select, insert, update, delete on public.recruiter_profiles to authenticated;
grant select, insert, update, delete on public.ai_conversations to authenticated;
grant select, insert, delete on public.candidate_bookmarks, public.job_bookmarks to authenticated;
grant select, insert, update on public.candidate_embeddings to authenticated;
grant select, insert on public.communication_logs to authenticated;
grant insert on table public.candidates to authenticated;
grant execute on function public.match_candidate_embeddings(vector, integer, double precision) to authenticated;

create index if not exists ai_conversations_user_updated_idx
    on public.ai_conversations (user_id, updated_at desc);
create index if not exists communication_logs_created_idx
    on public.communication_logs (created_at desc);
create index if not exists communication_logs_application_idx
    on public.communication_logs (application_id)
    where application_id is not null;

commit;
