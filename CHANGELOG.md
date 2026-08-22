# Changelog

## Unreleased

### Added

- Candidate editing, archive, and restore
- Job editing, close, archive, and reopen
- Interview rescheduling, cancellation, interviewer and meeting-link updates
- Interview change history in existing feedback JSON
- Communication History page using structured audit events
- AI Recruiter recent searches, session saves, export, and bookmarks
- Production architecture, security, feature, testing, and setup documentation
- AI Interview Copilot with session-only interview evidence
- Local candidate relevance search and pgvector migration proposal
- Validated CSV/XLSX candidate import and filtered export
- ADMIN, RECRUITER, and VIEWER UI/service guards
- Google/Outlook calendar event preview and OAuth boundary
- Database-first AI conversation, candidate/job bookmark, and communication-log adapters
- Review-only Phase 2 v1.1 Supabase migration

### Security

- Extended the review-only RLS migration with authenticated candidate and job
  update grants and policies
- Preserved the no-delete policy and unauthenticated app boundary
- Added service-layer permission enforcement and proposed role-aware RLS
- Kept Copilot transcripts session-only and prevented automated hiring decisions

### Changed

- Communication audits are emitted as JSON lines and include recruiter identity
- Existing business logic and AI query routing remain unchanged
