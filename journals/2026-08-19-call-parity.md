# 2026-08-19 — Call flow to the CodePen (30 / 30A / 34)

## Task

The live call connected but did not match the CodePen. Bring it to parity on both
platforms. Repos: `kotlin`, `swift`, and this one.

## What the audit flagged, and what I built

**Header — the attorney name.** The CodePen mock names "Rachel Whitmore". The call
response (`MemberCallResponse`) carries no name, and `member-client` deliberately
does **not** show one (backend **#138**: it shows "Licensed Attorney Connected."
because the member client cannot attest a real name). So the honest fix is not a
fabricated name — the header now reads **"Licensed attorney · connected"** (and the
"·" separator the app had been rendering as "-").

**Control bar — four actions, not two.** Was Mute / End. Now **Documents · Mute ·
Camera · End**, matching `member-client`'s own set. Camera is on/off, reaching the
publisher (`publishVideo`) the same way mute reaches `publishAudio` — a new
`VonageSession.setCameraEnabled` on both platforms, bridged from the view model.
(Icons: Android uses the existing `ic_wc_*` drawables; iOS uses SF Symbols.)

**In-call Documents sheet (30A).** New. Opens from the Documents control, lists the
member's own documents via the existing `listMyDocuments`. Every saved document is
already visible to the attorney for the call, so the rows are **read-only status**
("Visible to your attorney"), not share controls and not a mid-call uploader —
matching `member-client`'s reasoning. Empty state + Back to call. Persistent REC.

**PIN end-session gate (34).** New. **End** now opens the PIN pad **when the member
set a PIN** (`isPinSet` checked once when the call goes live); with no PIN it ends
directly. The entered PIN is checked with **`verifyMemberPin`** — added to both
`AsiApi`s, since only `isPinSet` / `setMemberPin` existed. The call stays live
behind the gate, so "Back to call" returns to a working call; a wrong PIN clears and
asks again. Test Call sessions get a "Forgot PIN?" help line; a real session has no
recovery path here by design (#138). Reuses the existing `AsiPinPad`.

**Ended copy.** Dropped "A recording is saved to your account" — members have no
access to recordings (#140). Now just "Your session has ended."

## API

All backed by operations already in `member-client`; only `verifyMemberPin`
(`mutation verifyMemberPin(userId, pin)`) needed adding to the native `AsiApi`s.
`listMyDocuments`, `isPinSet`, `setMemberPin` were already present.

## Verification

| Suite | Result |
|---|---|
| Android — `compileDebugKotlin` + `testDebugUnitTest` | **BUILD SUCCESSFUL**, all pass |
| iOS — build + `CallViewModelTests` | **BUILD SUCCEEDED**, **6 / 6** |

Not yet eyeballed on-device (emulator is down); a visual pass over all the parity
work is pending a relaunch.

## Commits

`kotlin dev 8e2ba48`, `swift main 00bddce`.

## Where CodePen parity stands

Done: **Situations** ([[2026-08-19-situations-parity]] — guidance card, gold eyebrow,
centred tiles) and **Call** (this). Remaining from the audit (the deliberate
2-column Home tiles are the one kept divergence):

1. **Glovebox** — masked read-only section detail + one Edit action (currently
   always-editable, raw PII); pill/copy fixes.
2. **Account** — Family dashed "Open member spot" cards; Settings pane (Language row,
   footnote, drop Replay-tour); remove the hub email; the "PIN & security" /
   "Support & intro video" hub rows need destinations (flag).
3. **Home** — remove the non-design extras (Connect-with chips, Open-Glovebox button,
   routing hint), fix the heading/link, build the grace state; keep the 2-col cards.
4. **Notifications** — split the merged centre + settings into two screens.
5. **Activity** — "Practice run" descriptor on Test Call rows (transcript stays a
   gap pending backend A1).