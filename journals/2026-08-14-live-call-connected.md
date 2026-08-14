# 2026-08-14 — The member↔attorney call connected (finally)

## Task

The backend answered our blockers doc: all five fixed, S2 (routing) with a
model change we had to adopt. They gave us a desktop attorney login
(`samson@ainnop.com`) and asked the one question that has hung over this project
since the start — **"let me know if you manage to connect between the member and
attorney."**

We did. For the first time on dev, a member's call reached an attorney's console,
was accepted, and opened a live video room.

## The one code change: auto-match sends neither hint

Their S2 correction: routing is **jurisdiction-wide by default**. A call with no
`attorneyId` and no `queueId` goes to any online attorney covering the caller's
jurisdiction. `queueId` is the premium/corporate dedicated-pool path only — and
our app had been sending it for every auto-match, which meant we were exercising
the premium path and a `409` from it meant "the curated pool is empty", not "no
attorney free".

Fixed in both apps: auto-match sends **neither** hint; `attorneyId` only on a
chip tap. Dropped the dev `QUEUE_ID`. Updated the CLAUDE.md routing contract and
warned against copying `member-client`, which still sends `queueId`.

- `kotlin`: `CallViewModel` — `queueId = null` always; constant removed.
- `swift`: `CallViewModel` — `queueId` dropped from the call.
- Tests updated on both (the "auto-match routes via the queue" test now asserts
  neither hint is sent). Android 416 / iOS 394, both green.

## The live call, end to end

1. **Desktop attorney** — built and ran `lfr-desktop` at the released
   `dev-v0.5.28` (the tag with the #149 fixes: online-without-a-queue, and
   visible poll failures). Logged in as `samson@ainnop.com`, went **online** —
   no queue needed, exactly as their fix intended. Presence stored as `online`
   (their ENUM-coercion fix; our old `"available"` writes had silently landed as
   `''`, which is why no attorney was ever routable).
2. **Member** — placed an auto-match call (no hints, US coordinates) as
   `munyira851`. `member-call` returned **HTTP 200** — the path that has returned
   `409` for as long as we have tested. Routed to Samson (the only online
   attorney), confirmed in his assignment poll as a real `ringing`.
3. **Attorney console** — the incoming call appeared in "Calls in Queue" and as a
   toast: *SAMSON PHILLIP · +16232008545*. Accepted it → the console went
   **On call**, opened the Vonage room, and **published live video** (Samson's
   camera self-view, camera indicator green). It showed *"Waiting for member…"*.
4. Ended the call cleanly — logged as **Picked up**, incident form ready for
   filing. Set Samson **offline** afterwards to leave dev tidy.

**What "Waiting for member…" means, honestly.** The attorney half is fully live —
routed, accepted, room joined, video publishing. The member half was an API call,
not a real Vonage video client, so there was no member stream for the attorney to
see. That is the one piece I could not drive: **the virtual devices cannot run
the video SDK.** The Android emulator ANR'd repeatedly trying to initialise it
(software rendering, no GPU video encode), and the iOS simulator has no camera at
all. A true two-way *picture* needs a physical phone. Everything up to and
including the attorney joining the room and publishing is proven.

## The location factor the backend flagged

They warned "location/country can be a factor," and it was the crux. Samson
covers **US (National)** and **Kenya (National)**; the member's jurisdiction is a
dev id (`de400000-…`) in a different org. Auto-match with the emulator's default
**US coordinates** routed to Samson anyway — routing used the location/country
match, not just the jurisdiction id. Worth remembering: auto-match depends on the
member's location resolving to a country an online attorney covers.

## Their other fixes, verified live

| Fix | Check |
|---|---|
| **S1** — member token on `commsUpsertAttorneyPresence` | now `forbidden` ✅ |
| **S3** — `mySessionStatus{status reason}` exists | returns `active` ✅ |
| **S3** — session supersede | the desktop showed the new **"Signed in on another device"** unlock screen when our probe logins superseded it — the honest message, working |
| presence with `state:"available"` | stored as `online` (alias accepted) ✅ |

**S3 bit us mid-test, correctly.** Every time we logged in via `curl` as
`munyira851` or `samson` to run a probe, it **superseded** the live session on
the emulator / desktop — the emulator went "unauthorized", the desktop showed the
lock screen. That is single-device enforcement doing exactly what we asked for.
The lesson for our own testing: one session per identity — drive the member from
the emulator and the attorney from the desktop, and stop minting probe tokens for
accounts that have a live client.

## What we owe the backend (relayed answer)

- **Yes — connected.** Auto-match routes to an online attorney and the console
  opens the live room. The routing fix is shipped in both apps.
- The only thing we could not show is a two-way *picture*, and that is our
  tooling (emulator/simulator can't run the video SDK), not their backend.
- Confirmed S1/S3 enforcement live; S3's supersede screen renders in the desktop.

## S3 — still to build in our apps

The backend wants clients to poll `mySessionStatus` and show the
"opened on another device" message on `superseded`. **Not yet wired in
`kotlin`/`swift`** — our apps still only learn of a dead session via a 401 on the
next request. Worth doing: poll on resume + every 60s, and show the accurate
message we already have copy for. Logged as the next item.

## Open issues / next steps

- **Wire `mySessionStatus` polling** (S3) in both apps — the one piece of the
  backend's response that lands on us as new work.
- A true two-way video **picture** needs a physical device; not achievable on the
  emulator/simulator.
- Desktop `lfr-desktop` is read-only for us — we ran the released `dev-v0.5.28`
  from a tag checkout; nothing committed there.

---

## Follow-up — `mySessionStatus` polling wired (S3), both platforms

The one new item the backend's response put on us. Now done.

**Both apps** now poll `mySessionStatus` on resume (Android `ON_RESUME`, iOS
`scenePhase == .active`) and every 60s while signed in — the backend's own
cadence. On `superseded` or `revoked` the session ends with an honest,
user-facing reason instead of the old bare 401:

> "You're now signed in on another device. Only one device can be active at a
> time."

carried to the login screen as a notice, email pre-filled.

Design decisions, matched across platforms:
- **`unknown` never signs anyone out.** An unrecognised status string is treated
  as active — a backend rename must not lock members out.
- **Deferred during a call.** A supersede while a call is on screen is not acted
  on mid-call — the "never mid-emergency" rule and the backend's own guidance
  ("finish it and sign out when it ends"). The 30-minute grace keeps the token
  alive; the next poll after the call ends signs out.
- **A failed status read never signs anyone out.** Only an explicit
  `superseded`/`revoked` from a *successful* read does; a network blip is
  ignored.

`AsiApi.getSessionStatus`, a `SessionStatus` enum, `refreshSessionStatus(onCall:)`
on the session manager, and a `notice` on the login screen — on both platforms.

**Verified live on Android:** signed in on the emulator, superseded the session
from elsewhere, backgrounded and reopened the app — it signed out to the login
screen showing the another-device notice, exactly as designed. **iOS** is
built + unit-tested (8 tests) but not driven live on the simulator; the logic
and wiring are identical to Android's, which was.

Tests: **Android 424 / 0**, **iOS 402 / 0** (8 new each).


## iOS parity check (2026-08-14 PM)

Ran the S3 flow on the iOS simulator headlessly (mcp simulator tools, so it
didn't touch the user's screen): signed in as `munyira851`, superseded the
session from elsewhere, backgrounded and foregrounded the app. The
scenePhase-active poll caught `superseded` and signed out to the login screen
showing the same notice as Android — *"You're now signed in on another device."*
Parity confirmed live on both platforms.

## Note on "the call isn't connecting" (main-branch build)

Diagnosed: auto-match returns **409** right now because **no attorney is online**
(Samson was set offline after the earlier live call). That is the routing change
behaving correctly — the app surfaces it as a retryable "no attorney available",
which can read as "not connecting". With the *same* main-branch code and Samson
online earlier today, the identical call returned 200 and connected. So:

- **A call only connects when an attorney is online** on the desktop (dev-v0.5.28).
- On a **simulator/emulator the video itself won't render** even when routed —
  the SDK limit — so the call screen would sit on "connecting". A real device is
  needed to see live video.

No regression in the routing code; the variable is simply whether an attorney is
online.
