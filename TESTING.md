# Testing

## Automated checks

Run from the project root:

```powershell
python -m compileall -q app.py components services
git diff --check
python -m unittest discover -s tests -v
```

To smoke-test Streamlit startup:

```powershell
streamlit run app.py --server.headless true
```

## Manual regression checklist

- Invalid credentials do not expose navigation or data.
- A valid login loads protected pages; logout returns to sign-in.
- Candidate edit persists; archive hides the candidate; Show archived and
  restore return it.
- Job edit persists; close, reopen, archive, and reopen-from-archive work.
- Interview reschedule, interviewer, meeting link, cancel, and status changes
  persist and create history entries.
- Confirmed email/WhatsApp sends appear in Communication history with retry and
  delivery metadata.
- AI suggested prompts and recent searches execute existing query behavior.
- Conversation save/export works and candidate bookmarks toggle correctly.
- Every page has a useful empty state and remains usable at narrow widths.
- ADMIN/RECRUITER permissions allow intended writes; VIEWER writes fail.
- Copilot preparation/follow-ups/evaluation use only stored or recruiter-entered evidence.
- Local relevance ranking never invents candidate content.
- Bulk imports reject malformed and duplicate rows; XLSX exports open successfully.
- Calendar creation and communications are mocked; no external side effects occur.
- AI conversation and bookmark storage falls back safely when migration tables are absent.

The Phase 2 suite uses Streamlit AppTest for all eleven authenticated pages and
the unauthenticated login boundary. External webhooks, calendar providers,
Supabase migrations, and production writes are never invoked by tests.

Never test production sends without an approved test recipient and webhook.
Never apply migrations automatically as part of tests.
