---
trigger: always_on
---
# SecondSense-Wealth Workspace Rules
These rules augment the global Windsurf rules for this repository and are **always on** unless explicitly overridden.

## 1. Testing
- **No mocking in integration tests** — rely on live Supabase/Test services.
- Mocking is permissible **only** in pure unit tests.
- All build/test commands must run via `make` targets (e.g., `make test`, `make test-integration`).

## 2. Supabase & Database
- All user management (create/update/delete) **must** use the Supabase Auth API; direct SQL to `auth.users` is prohibited.
- Inserts into application tables must include a valid `id` if the column lacks a default.
- Follow migration naming convention `supabase/migrations/YYYYMMDDHHMMSS_name.sql`.

## 3. Secrets & Security
- Never hard-code API keys or DB credentials.
- Secrets belong in `.env.secrets*` files and should be referenced via environment variables.
- Prompt the user before editing any secret file.

## 4. Memory Management
- Use `create-memory` to record architecture decisions, schema changes, and user preferences.
- Do **not** store sensitive data or credentials in memories.

## 5. Documentation Updates
- Update `docs/Decision_Log.md`, the architecture docs, and `memory-bank/contextSummary.md` after significant changes.
- Keep `TODO.md` current with migration tasks.

## 6. Code Hygiene & Refactoring
- Refactor files exceeding **300** lines.
- Remove unused imports and dead code in edits.

## 7. Communication Style
- Address the user as **"you"** and refer to yourself as **"I"**.
- Keep responses concise; avoid verbosity.


_Last updated: 2025-06-22_

