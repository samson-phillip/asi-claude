# 2026-08-27 — Call: react to a declined / unanswered call (stop hanging on Connecting)

## Task

Reported: when the LFR declines a call, the app stays on the Connecting screen
forever instead of reacting. Asked to check how the web member-client handles a
decline, then fix ours. Repos: `member-client` (read-only reference), `kotlin`,
`swift`.

## What the member-client does (after a `git pull`)

Pulled `member-client` (dev) — it had fresh work, incl. ~164 lines in
`CallScreen.tsx`. Key finding:

- **There is no explicit "declined" signal.** A decline and a no-answer are the
  same thing to the client: the attorney's stream never arrives. The client
  catches it with a **ring timeout** — `RING_TIMEOUT_SECONDS = 45` — that runs
  while `phase === "connecting"` and, if the attorney hasn't joined, calls
  `endCall("no-answer", …)`. That's a distinct phase (`no-answer`) from
  `no-attorney` (the immediate 409 when nobody is online), shown as "No attorney
  picked up" with a retry.
- The backend has its own `CANCEL_RING_TIMEOUT_SECONDS` (~30s) sweeper; the
  client's 45s sits just past it. A session disconnect during connecting is
  ignored (only a *live* call "ends"), so the timeout is the sole mechanism.

## The gap in our app

Our `CallPhase` was ported from an **older** member-client:
`starting | connecting | live | ended | no-attorney | error` — no `no-answer`.
And nothing moved the phase out of `Connecting` except the attorney's subscriber
connecting (`onPhase(Live)`) or an error. So a decline/no-answer → stuck on
Connecting indefinitely. Confirmed in `VonageSession`: a session disconnect with
no remote stream is (correctly) ignored, and it never emits `NoAttorney`.

## Change (both platforms)

- New **`CallPhase.NoAnswer`** (terminal, retryable), rendered as **"No attorney
  picked up." / "We couldn't reach an attorney in time. Please try again in a
  moment."** with Try again / Back — mirroring `no-attorney`.
- A **45s ring timeout** (`RING_TIMEOUT_SECONDS`), **armed by `onPhase(Connecting)`**
  (which `VonageSession.connect()` calls synchronously) and cancelled the moment
  the attorney joins (`Live`) or the call ends. If it fires while still
  connecting → `NoAnswer`. Arming on the video-layer's connecting signal (not on
  credentials) keeps the countdown tied to when ringing actually begins — and
  keeps `Connecting` a stable resting state for the unit tests, which don't
  create a video session.
- `canRetry` now covers `NoAnswer`.
- Kotlin: `onCleared()` cancels the timer; Swift: `deinit` cancels it and the
  Task is `[weak self]`.

## Verification

Emulator (`emulator-5554`), final build, **LFR online**:

| Step | Result |
|---|---|
| Test Call | rings out (Test Call doesn't route to the LFR) → NoAnswer ✓ |
| Traffic Stop (rings the LFR), left unanswered | Connecting → **"No attorney picked up"** + Try again ✓ |

Previously this hung on Connecting forever.

| Suite | Result |
|---|---|
| Android — `testDebugUnitTest` | **BUILD SUCCESSFUL** (5 failures caught + fixed; 2 tests added) |
| Android — `assembleDebug` (installed + driven) | **BUILD SUCCESSFUL** |
| iOS — build (iPhone 16 Pro sim) | **BUILD SUCCEEDED** |

The first test run **failed** (5 cases): the ring timeout fired under
`advanceUntilIdle()` (which skips the 45s delay), so tests treating `Connecting`
as a resting state saw `NoAnswer`. Fixed by arming on `onPhase(Connecting)` (the
tests don't drive the video layer), updating the terminal-states test to include
`NoAnswer`, and adding `an unanswered call times out to no-answer` +
`an attorney joining cancels the ring timeout`.

## Product note

Because there is no explicit decline signal (same as member-client), a decline
reflects only when the ring window closes — a member can wait ~45s on Connecting
after the LFR has already declined. Matching the web is correct for now; a
faster, instant-decline experience would need a backend decline push (a separate
ask — the web doesn't have it either).

## Files

- **kotlin** — `core/video/CallPhase.kt`, `feature/call/CallViewModel.kt`,
  `feature/call/CallScreen.kt`, `feature/call/CallViewModelTest.kt`.
- **swift** — `Core/Video/CallPhase.swift`, `Feature/Call/CallViewModel.swift`,
  `Feature/Call/CallScreen.swift`.
