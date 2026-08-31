# Innocent's ASI 2.0 platform feedback (2026-07-28) — mobile-app triage

**Source:** "ASI 2.0 Feedback-Questions 07282026" (shared 2026-08-31, "for your
consideration").

## What this document is

A platform-wide feedback/requirements pass. The vast majority is **not the native
mobile apps** I own (`kotlin`/`swift`):

- **I. Admin Panel** (Masters, Workforce, RBAC, App Settings, Finance) → the admin
  panel repo — Innocent/backend.
- **III. Consultant Desktop App** (password reset, default Online toggle, red
  logout ribbon) → `lfr-desktop` — **read-only reference for me, not mine to build.**
- **Finance / Promo Codes / Reporting / static-DB sync** → backend + admin.
- **IV. Mobile Apps and Web Mobile App → "NOT YET EVALUATED."** Innocent hasn't
  reviewed the native apps yet, so there is no direct mobile task list here.

So I am **not** actioning the bulk of this. Below is only what touches the native
apps, with status + dependency. Almost all of it is **backend-first** (the admin
must serve the data before the app can render/honour it) or **"let's discuss"**.

## Mobile-relevant items

| # | Item (doc ref) | Mobile impact | Status / dependency |
|---|---|---|---|
| 1 | **Account-status taxonomy** — Member / Trial Member / Member Lead / Guest User (II) | This IS the `myAccountStatus` segmentation the app's gate already keys on. | **Already aligned.** Confirms the model; no change. Also **confirms the open trial bug**: a *paid conversion* must become **Member** (membership off `trial`) — exactly the backend gap in `notes/backend-trial-conversion-not-settling-for-innocent.md`. |
| 2 | **Financial Status** — Current / Grace Period / Expired / Canceled (II.1.e) | Maps 1:1 to the app's grace / expired / payment-failed / canceled gate states. | **Already implemented** (AccountGate). Worth confirming the field names when the backend formalises them. |
| 3 | **Sanctions "Disable" flag = call block** (II.1.f) | A NEW, overriding gate: when set, the member must be **blocked from requesting legal support**. The app has **no such signal today**. | **Gap, backend-first.** Needs the field on the account/entitlement API, then a gate branch (like `connectBlocked`) + a clear "support paused" message. High-value safety control — flag to wire once the backend exposes it. |
| 4 | **Enrollment Status** — …Active = confirmed PIN → full home/app access (II.1.c) | Ties to onboarding + the PIN. The app already gates setup and nudges the PIN. | Mostly aligned; revisit if the backend makes "Active" a hard precondition for the home page. |
| 5 | **Admin-configured call messages** (App Settings 1.a; Figure 1) — "unanswered call" / "call timeout" messages shown to the member while connecting | The connecting screen's wait/timeout copy (`CallWatch.waitNotice`) is currently **hardcoded** ("Still connecting you — trying the next available attorney…"). Doc wants these admin-authored + time-tiered (15s/30s/60s). | **Enhancement, backend-first.** When comms/admin serves these strings, drive the connecting screen from them instead of the constants. |
| 6 | **Document types / fields / icons / display order** (Masters 7; App Settings 5) — new fields (state_of_issue, gun_owner, health_conditions), type icons, and admin-set ordering "don't appear in the mobile app" | Glovebox categories/icons/fields. | **Backend-first / likely member-client.** The complaints are about the *web* mobile app and admin→API plumbing. Confirm whether the native Glovebox renders admin-configured types/fields/order from the API, then close any native rendering gap. |
| 7 | **Gender options** — hardcode Male / Female / **Other**, translatable (II) | The app already **hardcodes** gender (`Gender` enum: male/female/unspecified) — it does not pull from config, so it already matches the intent. | **Small, self-contained.** Only deltas: confirm the third option reads "Other" (vs "unspecified") and is translated. Could do on request. |
| 8 | **Promo codes** on checkout (Finance; David 1.1) | The native apps have **no in-app checkout** (members go to web), so promo entry is member-client/web. | **N/A for native** (already noted in the David pass). |

## Recommendation

- **Nothing here needs native-app code today.** Items 1–2 are already aligned;
  3, 5, 6 are backend-first (the admin/API must serve the data before the app can
  act on it); the rest is other teams' scope.
- **Two to actively track** as backend contracts land, because they change app
  behaviour: **(3) the Sanctions call-block** (a real gating control) and
  **(5) admin-authored connecting/timeout messages**.
- **One small self-contained mobile item** available now if wanted: **(7)** tidy
  the gender third option to "Other" + translation.
- This doc **reinforces the trial-conversion write-up**: the account-status model
  says a paid conversion = **Member**, i.e. the membership must leave `trial` —
  which is precisely what isn't happening and what I asked Innocent to fix.

For the "let's discuss" items, the mobile-side questions worth putting to Innocent
are: what account/entitlement **fields** will carry Sanctions and Financial
Status, and whether the connecting-screen messages will come from comms per-call
or from static admin config.
