# 2026-08-10 — Project Setup

## Task
Clone the four ASI 2.0 repositories under `ASI_2/` and set up `asi-claude` as the
Claude working repo per the project instructions in `asi-2-0.md`.

## Goal
A working environment where Claude starts each session authenticated as
`samson-phillip`, knows the repo roles and their write permissions, and has a
journal trail to recover context from.

## What was done

### 1. GitHub auth
`gh auth switch --user samson-phillip`

Two accounts are configured on this machine — `samson-mm` (was active) and
`samson-phillip`. Switched to `samson-phillip`; it is now the active account.
**This switch is per-machine state, not per-session** — verify it at the start of
every session, since anything else on the machine can flip it back.

### 2. Repositories cloned
All four cloned into `/Users/samsonphillip/attorney/ASI_2/` as siblings of
`asi-claude`:

| Repo | Commits | State |
|---|---|---|
| `swift` | 1 | README only — greenfield |
| `kotlin` | 1 | README only — greenfield |
| `lfr-desktop` | 8 | Wails app (Go + `frontend/`) |
| `member-client` | 1 | Vite + React 18 + TS, `src/` populated |

All on `main`.

### 3. Working repo configured
- **`CLAUDE.md`** — startup checklist, repo permission table, source-of-truth
  notes, and the reference API surface distilled from
  `member-client/src/lib/api.ts`.
- **`.claude/settings.json`** (committed) — enforces the permission model at the
  harness layer rather than relying on instruction-following:
  - `additionalDirectories` for all four sibling repos — required, since they sit
    outside the `asi-claude` working directory and are otherwise unreachable.
  - `allow` Read across `ASI_2/**`; Edit/Write scoped to `kotlin/**` and
    `swift/**`.
  - `deny` Edit/Write on `lfr-desktop/**` and `member-client/**`.
- **`.gitignore`** — `.DS_Store` (one was sitting untracked) and
  `.claude/settings.local.json`.
- **`journals/`** — created; this is the first entry.

## Decisions and why

**Deny rules instead of a written-down rule.** The spec marks `lfr-desktop` and
`member-client` read-only. A `deny` rule fails the write closed; a line in
CLAUDE.md only works while it stays in context. Deny beats allow in Claude Code
permission resolution, so the rule holds even under a broader allow.

**Project settings, not local settings.** The permission model comes from the
project spec and should travel with the repo, so it went in the committed
`.claude/settings.json`. `settings.local.json` is left for personal overrides and
is now gitignored.

**Corrected a repo name.** The spec's table says `lrf-desktop`. The actual repo
is **`lfr-desktop`** (`f` before `r`) — the clone command in the request used the
correct spelling. Noted in CLAUDE.md so the wrong name doesn't get typed later.

## API endpoints used
None called. Catalogued for future work from `member-client/src/lib/api.ts`:
- GraphQL `POST /query` — `login`, `user`, `casesByUser`,
  `adminIncidentTypeList` + `adminLanguageList`, `partnerAttorneys`
- REST `POST {API_BASE_URL}/api/vonage/video/member-call` — returns Vonage video
  credentials; `409` = no attorney available

## Test results
No tests — no application code was written. Verification performed:
- All four clones present on `main` with the commit counts above.
- `jq -e` parses both `.claude/settings.json` and `.claude/settings.local.json`;
  deny and `additionalDirectories` arrays confirmed present.
- `gh auth status` confirms `samson-phillip` is the active account.

## Open issues / next steps
1. **Deny rules cover Edit/Write, not Bash.** A shell redirect or `git checkout`
   inside the reference repos would still land. Treat "never modify" as a
   standing rule for shell commands too.
2. **Settings reload.** `.claude/settings.json` was created mid-session. If the
   deny rules don't appear to take effect, the config needs a reload —
   restart, or open the hooks/config panel once from an interactive terminal.
3. **`kotlin` and `swift` need scaffolding.** No Gradle/Xcode project, no test
   harness. First real task should stand up project structure plus a unit-test
   target, since the spec requires unit tests for every screen.
4. **`member-client` has no test setup either** — no test runner in
   `package.json`. It is read-only, so tests for it are out of scope; note it if
   behaviour parity ever needs asserting programmatically.
5. **Reference app not yet run.** `npm install && npm run dev` in
   `member-client` is untried; it expects a reverse proxy (`serve-proxy.mjs`) for
   `/query` and `/api/*`. Verify before relying on it as a live reference.
6. Auth flow to mirror: login returns `accessToken` + `refreshToken`, but
   `api.ts` only ever sends `accessToken`. **No refresh logic exists in the
   reference** — decide how `kotlin`/`swift` handle expiry.
