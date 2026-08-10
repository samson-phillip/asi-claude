# Project Instructions — ASI 2.0

## Working Repository
`asi-claude` is the working directory for this project. All journals, notes, and
scratch work live here. Always operate from this repo.

Absolute path: `/Users/samsonphillip/attorney/ASI_2/asi-claude`

## Startup Checklist (run before ANY code or task)
1. `gh auth switch --user samson-phillip` — required before any git command.
   The machine also has a `samson-mm` account; it is **not** the one to use here.
2. Confirm you are in the `asi-claude` working directory.
3. Read the latest journal entries in `journals/` to recover context from
   previous sessions.

## Repositories and Permissions
All five repos are siblings under `/Users/samsonphillip/attorney/ASI_2/`.

| Repo | Role | Permission |
|---|---|---|
| `asi-claude` | Working repo — journals, notes, planning | Read/write |
| `kotlin` | Android app source | Read/write |
| `swift` | iOS app source | Read/write |
| `lfr-desktop` | Reference only | **Read-only — never modify** |
| `member-client` | Reference only | **Read-only — never modify** |

Write code only in `kotlin` and `swift`. Use `lfr-desktop` and `member-client`
as references for behaviour, structure, and API usage.

> Naming note: the original spec wrote this repo as `lrf-desktop`. The actual
> repo on GitHub is **`lfr-desktop`** (`Attorney-Shield-Inc/lfr-desktop`).

### Current state of the app repos
`kotlin` and `swift` are **greenfield** — each is a single commit containing only
a `README.md`. There is no existing app scaffolding, build config, or test
harness. Expect to create the project structure as part of the first real task.

- `kotlin` — "Android 2.0"
- `swift` — "iOS Swift 2.0"

## Source of Truth
`member-client` is the mobile web application and is the reference
implementation for both mobile apps. Match its screens, flows, and behaviour
unless told otherwise. Additional design files will be supplied as needed.

`member-client` already has working API integrations. Reuse the same endpoints,
request/response shapes, and auth flow in `kotlin` and `swift`. **Do not invent
new endpoints.**

### Reference stack
- React 18 + TypeScript + Vite; `@vonage/client-sdk-video` for the video call.
- Screens: `LoginScreen` → `HomeScreen` → `CallScreen` (`src/screens/`).
- Session/auth state: `src/state/session.tsx`.
- API client: `src/lib/api.ts`. Runtime config: `src/lib/config.ts`.

### API surface (read `member-client/src/lib/api.ts` before wiring anything)
Two backends, reached same-origin behind a reverse proxy:

- **GraphQL gateway** — `POST /query` (`GRAPHQL_URL`). Bearer token in
  `Authorization` when authenticated. Operations in use:
  - `login(input: LoginInput!)` → `accessToken`, `refreshToken`, `userID`, `roles`
  - `user(id: ID!)` → `organizationID`, `displayName`, `email`
  - `casesByUser(userID:, limit:)` → member cases
  - `adminIncidentTypeList(activeOnly:)` + `adminLanguageList` → incident tiles
  - `partnerAttorneys(partnerId:, limit:, offset:)` → selectable attorneys
- **Comms REST** — `POST {API_BASE_URL}/api/vonage/video/member-call` → returns
  `callId`, `videoRoomId`, `apiKey`, `sessionId`, `token`. No auth today.
  `409` means no attorney available (`NoAttorneyError`) — surface it as a
  retryable message, not a crash.

Behaviour worth carrying over verbatim:
- Routing: send `attorneyId` when the member pre-selected one, **else** `queueId`.
- Incident-type labels are multilingual — pick English, then the org default
  language, then first available, then a humanized `code`.
- Location is best-effort: never block placing a call on geolocation.
- `listAttorneys` never throws; an empty list means auto-match/queue only.
- Dev seed defaults (org, jurisdiction, queue IDs) live in `config.ts`
  `DEV_DEFAULTS`.

## Testing
- Write unit tests for every screen you build.
- Launch the Android Emulator, iOS Simulator, and Claude Browser (pointed at
  `member-client`) to verify feature behaviour against the reference app.
- Save test reports as journal entries.

To run the reference app locally:

```bash
cd /Users/samsonphillip/attorney/ASI_2/member-client && npm install && npm run dev
```

## Journaling (required for every task)
For each task, create a Markdown file at:
`journals/YYYY-MM-DD-<short-task-name>.md`

Each entry must include:
- Task description and goal
- Repos and files touched
- Decisions made and why
- API endpoints used
- Test results (pass/fail, coverage notes)
- Open issues or next steps

Journals are the memory for this project. **Write them as you go, not at the
end.**

## Git
Commit and push work to the `asi-claude` remote periodically — at minimum after
each completed task or journal entry.

Remote: `https://github.com/samson-phillip/asi-claude.git`
