# 2026-08-27 — Adopt C1: the real-time member call-state watch

## Task

Backend shipped **C1** (the real-time declined/no-pickup signal we asked for) to
dev + uat — `commsMemberCallState(callId)` query **and** a `call-state` Vonage
session signal (same payload). Innocent's reply
(`Downloads/2026-08-27-member-call-state-signal.md`) also flagged our **45s ring
timer as a live defect**: it is shorter than comms' re-ring budget (5 attorneys /
180s), so it could cut a member off at 45s while comms was still ringing attorney
3 of 5. Adopt C1 on both apps and drop the relative timer.

Repos: `kotlin`, `swift`. Spec: Innocent's doc (member-client `callWatch.ts` /
`CallScreen.tsx` `applyCallState` could not be pulled — the org remote 404s under
our account — but the doc is a complete spec: query fields, signal payload, the
`isFinal`-only rule, the safety-net formula, and §6 pseudo-code).

## The rules adopted (backend C1)

1. **A decline is not an ending.** `isFinal` is the ONLY field that leaves the
   connecting screen. A decline arrives `state=RINGING, isFinal=false,
   willKeepTrying=true` while comms re-rings; leaving on `ATTORNEY_DECLINED`
   would abandon the member seconds before a pickup.
2. **`lastEvent` is narration, not a decision.** We show "Still connecting you —
   trying the next available attorney…" on a decline/ring-out while
   `willKeepTrying`, "<name> is joining your call…" on `CONNECTED`, and say
   nothing once the budget is spent.
3. **Drop the 45s relative timer.** The only local timer now is an *absolute*
   safety net measured from the start of the wait:
   `deadline = max(waitStart + 45s, ringExpiresAt + 8s)`, only ever pushed later
   (never re-armed per poll — a re-armed deadline slides forward forever when an
   accepted attorney never joins).
4. **No client write on `isFinal`.** §4 says stop writing `commsUpdateCallState`
   when leaving on `isFinal` — and **our app never wrote call-state at all**
   (grep-confirmed), so this is satisfied by construction. The safety net just
   flips the UI to a retryable no-answer; comms has by then recorded the outcome
   itself (the net only fires *after* `ringExpiresAt + 8s`, or when comms is
   unreachable — in which case a write could not land anyway).

## Design

- **Pure `CallWatch`** (`core/video/CallWatch.kt`, `Core/Video/CallWatch.swift`) —
  `decide(snapshot) -> Waiting(notice) | NoAnswer | Ended`, plus `notice`,
  `safetyDeadline`, and lenient RFC3339 parsing. All the rules live here, testable
  without a view model, socket, or clock (member-client's `callWatch.ts` split).
- **One `applyCallState`** in the view model — poll and signal both feed it, so
  exactly one thing decides to leave the wait. Last-write-wins on a full snapshot
  (the signal can arrive out of order); foreign call ids and post-live snapshots
  are ignored.
- **The watch is armed in `onPhase(.connecting)`** (as the old timer was), so it
  is tied to when ringing begins and stays out of unit tests that never drive the
  SDK. The poll loop carries the safety net; `pollAfterMs` from the payload sets
  the cadence.
- **The `call-state` Vonage signal** is delivered through a new `onSignal` on the
  session wrapper (`Session.SignalListener` / `OTSessionDelegate
  session:receivedSignalType:fromConnection:withString:`), decoded by
  `AsiApi.decodeCallStateSignal`, and fed to `onSessionSignal` on the VM.
- **Live is still driven by the video stream** (a remote participant = the
  attorney). C1 drives the *failure* exits (no-answer / cancelled) and the
  connecting-screen narration; `CONNECTED` narrates "is joining" and waits for the
  stream, with the safety net as backstop for an accept that never joins.

## API endpoints used

- `commsMemberCallState(callId)` — new read (poll). Member-scoped; a member may
  only read a call they placed. `null`/error both mean "ask again", never "ended".
- `call-state` Vonage session signal — same payload, ~1s latency.
- No new writes.

## Test results

| Suite | Result |
|---|---|
| Android `testDebugUnitTest` (full) | **BUILD SUCCESSFUL** — new `CallWatchTest` (11) + reworked `CallViewModelTest` C1 cases (decline-not-ending, final no-answer, foreign id, post-live ignore, safety net via virtual clock) |
| iOS `xcodebuild test` (AttorneyShieldTests) | **TEST SUCCEEDED** — new `CallWatchTests` + `CallViewModel` signal cases |
| Android emulator | Installs, launches, Home renders — no startup regression from the call-flow changes |

## Not done / next steps

- **Live decline end-to-end unverified.** Needs a working dev session (the
  emulator's was stale/`unauthorized`) and an online LFR to decline on
  `lfr-desktop`, then watch `ATTORNEY_DECLINED → ringAttempt++ → CONNECTED/NO_ANSWER`
  per Innocent §7. The unit tests cover the decision logic; the poll/signal
  transport is thin.
- **Swift safety-net timing** is covered by the pure `safetyDeadline` test, not a
  VM timing test (no virtual scheduler for `Task.sleep`); the Kotlin VM test
  exercises the timed path via an injected virtual clock.
- Member-cancel/`member_pin` writes: member-client writes these; our app never
  has (out of C1's scope — C1 is the decline/no-answer *read*). Left as-is.
