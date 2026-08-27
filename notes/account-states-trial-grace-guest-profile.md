# Account states on the connect path — CodePen vs member-client vs backend vs app

**Date:** 2026-08-27
**Trigger:** A **trial** account (`x1@…`) signs in, taps to connect, and lands on the
plain **Connecting** screen — no LFR is rung, no trial modal appears. Per the CodePen,
a trial (and grace/guest/expired) tapping to connect should hit a **nudge/modal**, not a
normal call. This profiles each account state across the four sources so we know what to
build and what to ask the backend for.

---

## 1. Root cause of the reported symptom

`Home` decides whether to gate the connect action on **one** signal:

- `HomeUiState.isTrial = membership?.isTrial` and
  `Membership.isTrial = statusCode.equals("trialing")` (`AccountModels.kt:90`), where
  `statusCode = myMembership.status.code` (`AsiApi.kt:1024`).

But the backend's trial value is **not** `"trialing"`:

- `member-client` treats a trial membership as `statusCode` **`"trial"`** —
  `guest.tsx:114` gates on `["active", "trial"].includes(plan.statusCode)`.
- The authoritative post-login segmentation is **`myAccountStatus.code == "trial_member"`**
  (`api.ts:867`, `guest.tsx:111`), with a separate **`financialStatus`**
  (`current | grace_period | expired | canceled`, `api.ts:869`).

So `isTrial` is **always false** → the V2 gate (which the app *has* built, `TrialViewModel`
/ `TrialFlow`) never opens → the trial member falls through to a normal `member-call`.
The backend accepts it but does not route a trial to an LFR (nobody is notified), so it
sits on Connecting — now → "No attorney picked up" after the 45s ring timeout we just
added. **The app is checking the wrong field, and ignoring the segmentation it already
fetches.**

Corroborating: the app **already loads** `myAccountStatus` into the session
(`SessionManager.kt:171,225`, stored as `MemberContext.accountStatus`) — but **nothing
consumes it** (grep for `accountStatus` across `feature/` is empty). The entitlement
(`membershipEntitlement { entitled, graceUntil }`) is read only by the Account screen
(grace label) and `TrialViewModel`, never by the connect path.

---

## 2. The state matrix

Backend segmentation = `myAccountStatus.code` × `financialStatus`, plus
`membershipEntitlement.entitled` (the "may consult now" gate — the backend's own guidance:
*"entitled is the one to gate on, never the status string"*, `AccountModels.kt:110`).

| State | Backend signal | CodePen design | member-client behaviour | App today | Gap |
|---|---|---|---|---|---|
| **Guest** (never bought) | `code = guest_user` / `member_lead`, not entitled | **G1–G3**: home is browsable with a guest pill; every member feature opens the **G3 upsell** → trial (V1) or plans (04); "Not now" stays put | `guest.tsx` gate: upsell sheet *"Purchase a plan or start a free trial…"* on tiles/tabs/rows; never bounces out; `isGuest = (guest_user\|member_lead) && !holdsProduct` | **Not built.** No guest pill, no gate; a guest taps connect → normal call | Build the guest gate (member-client `guest.tsx` is the reference) |
| **Trial** | `code = trial_member`; membership `statusCode = "trial"`; entitled = true | **V2 gate**: tap shield/tile → *"You're on a trial"* → **pay to connect (T5–T8)** or **free AI demo** | **No V2 gate** — a trial *holds a product*, so the guest gate lets it **connect like a member** | **V2 gate built but never fires** (wrong signal) → connects to nobody | Fire the gate off the right signal; **product decision** below |
| **Active member** | `code = member`; entitled = true; `statusCode = "active"` | Normal connect | Normal connect | Normal connect ✓ | — |
| **Grace** (renewal failed, cover still running) | entitled = true + `graceUntil` set; `financialStatus = grace_period` | **Screen 35** grace Home + renew nudge | Account/Plan shows status; still entitled → can connect | Account screen shows **"GRACE PERIOD"** (`isInGrace`); **connect path unaffected** | Decide: warn-and-allow vs nudge to settle; wire to connect path |
| **Expired / canceled** | `financialStatus = expired`/`canceled`; **not** entitled; `code` still `member` | **Screen 35** expired Home → renew | *Not* caught by the guest gate (code=`member`) → likely reaches a refused call (a member-client gap too) | No handling → normal call | Block the connect with a **renew** prompt; needs the entitlement gate |

---

## 3. Recommendation for the app

**Gate the connect action on `membershipEntitlement.entitled` + `myAccountStatus`, not on
the membership status string.** Concretely, when the shield / a tile is tapped:

1. `code == guest_user || member_lead` (and not entitled) → **guest upsell** (G3).
2. `code == trial_member` (or membership `statusCode == "trial"`) → **V2 trial gate**
   (already built — just reached correctly).
3. `entitled == true` → **connect** (covers active, and grace while cover runs).
4. `financialStatus in (expired, canceled)` / not entitled and not guest/trial → **renew
   prompt** (screen 35).

This mirrors member-client's "gate on entitlement + segmentation, never the status
string," and it makes the V2 gate the app already has actually fire.

### Immediate low-risk fix (the reported symptom)
Make trial detection recognise the real signal: `myAccountStatus.code == "trial_member"`
(already in the session) **or** membership `statusCode in {"trial","trialing"}`, rather
than `"trialing"` alone. That alone restores the V2 gate for trials.

---

## 4. Product decision needed

**CodePen and member-client disagree on trials.** The CodePen gates a trial's call attempt
behind V2 (pay-to-connect or AI demo); member-client lets a trial **connect** like any
member (it holds a product). The app has the V2 gate built, and the request here is for
the CodePen behaviour — but this is a **Product call**, because the behavioural reference
does the opposite. If we gate, a trial cannot have a live consult until they convert; if
we connect, we match the web. Needs Product to pick one.

---

## 5. Questions / asks for the backend

1. **What is the authoritative, reliable "this account is a trial" signal for an account
   just created through the app's own trial signup?** `myAccountStatus` returns **null**
   for accounts the reconcile pass hasn't segmented yet (`AsiApi.kt:340` / member-client
   `api.ts:836`), and `myMembership.status.code` appears to be `"trial"`, not the
   `"trialing"` we coded to. If a fresh app trial can be *unsegmented* (null status) for a
   window, the app needs a signal that is correct immediately — otherwise a brand-new
   trial is unclassifiable right when they first tap to connect. **Please confirm the
   field + value the app should trust, and whether it is populated synchronously at
   signup.**
2. **Does routing reject a `member-call` from an unentitled member (trial not converted,
   expired, canceled)?** If the app's gate is bypassed or lags, the connect should
   **fail safe** — a refusal we can surface — not a room that rings no one. Today an
   ineligible member reaches a live room that is never answered.
3. **Is there a single "may this member consult right now" truth we should gate on?**
   `membershipEntitlement.entitled` looks like it (grace-aware via `graceUntil`); please
   confirm it is the intended gate for the *call* path and that trials read `entitled =
   true` during the trial (so the difference between "trial" and "active" is purely the
   V2 gate, not entitlement).

---

## 5a. Resolution (2026-08-27) — the three questions, answered by the updated member-client

The updated `member-client` gates all four states client-side, and reading how it
does it answers the questions above without waiting on the backend. It does **not**
depend on the backend rejecting an ineligible call — it prevents the call.

- **Q1 (reliable trial signal for a fresh app trial).** member-client's trial gate
  (`state/trial.tsx` + `lib/trialGate.ts`) does **not** use `myAccountStatus`
  segmentation at all. It reads `myMembership.status.code` (`isTrialStatus` ==
  `"trial"`) through a **three-value** `TrialKnowledge` (`trial | not-trial |
  unknown`) and **fails CLOSED**: `shouldGateLiveCall = knowledge !== "not-trial"`,
  so a null/unresolved/failed membership read still gates. There is therefore **no
  need for a synchronous segmentation signal** — an unsegmented fresh trial is
  gated by the fail-closed default, and the gate's copy switches to "Confirm your
  membership" for the `unknown` case (a convert on an already-active membership is
  an idempotent server no-op, so a real member is never double-charged).
  → *App:* we OR the membership status (`trial`/`trialing`) with the
  `trial_member` segmentation. member-client's stricter fail-closed-on-unknown is
  noted as a possible hardening, but our OR already fixes the reported bug.
- **Q2 (does routing reject an unentitled call?).** Moot for the client: member-client
  never lets an unentitled non-guest reach the call. It replaces the tiles with a
  renew/payment card (`!canCall && !isGuest`) or a payment-failed card, and gates
  guest/trial before `connect()`. So the client fails safe **by construction**,
  independent of backend behaviour. (Whether the backend *also* rejects server-side
  is still worth confirming as defence-in-depth, but is no longer blocking.)
- **Q3 (single "may consult now" truth).** Two layers, both from member-client:
  `canCall = ent.entitled || statusCode ∈ {active, trial}` decides whether to show
  the tiles at all; the **live-attorney** gate is `canConnectLive = entitled &&
  status != trial`, because a trial is entitled but must convert first. So the
  trial/active difference is purely the V2 gate, not entitlement — confirming a
  trial reads `entitled = true`.

**All three are answered by the behavioural reference; no backend change is required
to ship the client gating.** The one remaining backend ask that stands is the
separate real-time **decline/no-pickup** signal — see
[`backend-ask-call-decline-no-answer-signal.md`](backend-ask-call-decline-no-answer-signal.md)
(the ring timeout is the interim; a push signal would be faster than 45s).

## 5b. What is now built (2026-08-27)

Ported member-client's connect-path gating to both apps (`kotlin`, `swift`):

- **Guest** (`guest_user`/`member_lead`, no product) → guest pill + locked tiles +
  a **guest upsell sheet** on tap. "View pricing plans" hands off to the web
  checkout (the Welcome screen's existing `planUrl`), since there is no native
  checkout funnel (dev-plan §3); "Keep exploring" dismisses without leaving Home.
- **Trial** → the V2 gate (already built), now fired off the corrected signal.
- **Grace** → a gold "Grace period" pill + a non-blocking "Pay now" card (→ Account,
  where the card on file lives); the member still connects.
- **Expired / canceled** → tiles replaced by a "Choose a plan" renew card
  (→ web checkout); the shield/tile tap is walled off to Account.
- **Payment failed** (`past_due`, not entitled) → "We couldn't process your payment"
  card (→ Account).
- The gate is evidence-based and **fails OPEN**: two failed reads never hide the
  tiles from a covered member (the ring timeout now catches any stray unroutable
  call, so fail-open is safe). Everything waits on `accountLoaded` so no state
  flashes mid-load. Pure logic lives in `HomeUiState` (Kotlin) / `AccountGate`
  (Swift), each with a unit-test twin.

## 6. Files (for the fix, when the product call is made)

- `feature/home/HomeViewModel.kt` — `isTrial`, `membership`, and a new
  entitlement/segmentation gate on `onOpenTray` / `onTileTapped`.
- `feature/home/HomeScreen.kt` + `MainActivity.kt` — guest / renew sheets on the connect
  path (trial V2 gate already wired).
- `core/network/AccountModels.kt` — `Membership.isTrial` value; possibly derive the gate
  from `accountStatus` + `entitlement` instead.
- Swift mirrors: `Feature/Home/HomeViewModel.swift`, `AttorneyShieldApp.swift`,
  `Core/Network/AccountModels.swift`.
