# Mobile-side questions for Innocent — from the 2026-07-28 platform feedback

**To:** Innocent
**From:** Mobile team
**Re:** The native-app (iOS/Android) items in "ASI 2.0 Feedback-Questions
07282026". Most of that document is admin-panel / consultant-desktop / backend
scope; below are only the points where the **native apps need something from the
backend or a decision** before we can build. Each says what the app will do with
the answer.

---

## 1. Sanctions — the "Disable" call-block (II.1.f)

You describe Sanctions as an overriding flag that blocks a member from requesting
legal support. The apps have **no such signal today**.

- **What field carries it, and where?** On the account, the membership, or the
  entitlement — and what's the field name/shape (`sanctioned: bool`?
  `canRequestSupport: bool`?)?
- Is it exposed on the same reads the app already makes (`myMembership` /
  `membershipEntitlement` / `myAccountStatus`)?

**What we'll do with it:** add a gate branch (like today's "coverage lapsed"
block) that disables the connect button and shows a neutral "support is paused on
your account — contact support" message, ahead of the trial/guest/expired checks.

## 2. Financial Status field (II.1.e)

The app already implements the *behaviour* of Current / Grace / Expired /
Canceled (from the entitlement's `entitled` + `graceUntil` + membership status).

- When you formalise **Financial Status** as its own field, what are the exact
  values and which read carries it? We'd rather key on it directly than infer it,
  if it becomes authoritative.

## 3. Trial → Member conversion signal (cross-ref)

Already raised in `backend-trial-conversion-not-settling-for-innocent.md`, and the
account-status model in this doc **confirms it**: a paid conversion should become
**Member** (membership off `trial`).

- **What is the authoritative "this trial has converted" signal** the app should
  key on? We currently use `membership.statusCode != "trial"`. If it should be a
  specific status value, or `invoice.status == "paid"`, tell us and we'll use it —
  for both the gate and the "settlement confirmed" check.

## 4. Connecting-screen / call-timeout messages (App Settings 1.a, Figure 1)

You want the member-facing "unanswered call" / "call timeout" messages to be
admin-authored and time-tiered (15s / 30s / 60s). Today the app's connecting
screen uses **hardcoded** copy ("Still connecting you — trying the next available
attorney…").

- Will these strings be delivered **per-call by comms** (e.g. on
  `commsMemberCallState`) or as **static admin config** the app fetches once?
- What are the tiers/keys (a list of `{afterSeconds, message}`)?

**What we'll do:** drive the connecting screen's wait/timeout notices from that
source instead of the constants, keeping a hardcoded fallback for when it's
unavailable.

## 5. Documents — new fields, icons, display order (Masters 7; App Settings 5)

You noted new document fields (`state_of_issue`, `gun_owner`,
`health_conditions`), type icons, and admin-set ordering **not appearing in the
mobile app**.

- Are those complaints about the **web mobile app (member-client)** specifically,
  or the **native apps** too? (We can then confirm whether the native Glovebox is
  missing a rendering path vs. the API simply not returning the data yet.)
- Does the document-types/fields API expose a **display-order** field and the
  **per-type field list** the app should honour? If so, what are the field
  names?

**What we'll do (native):** render document categories, icons and fields from the
API in the admin-defined order, once the API returns them.

## 6. Gender — confirming the wire contract (II, Gender Options)

We've already **hardcoded the app's gender options to Male / Female / Other** per
your note (dropping "Non-binary" and "Prefer not to say" from the picker).

- Please confirm the **gateway `Gender` enum is standardising on `male` / `female`
  / `other`** so our wire values match. If the backend keeps other values, tell us
  the canonical set.
- "Subject to language translation" — the native apps have **no UI-localisation
  layer yet** (all copy is English). Translating gender labels specifically would
  need an app-wide i18n decision; flagging that as a separate, larger workstream
  rather than something we've done here.

---

## Summary of what's blocked on you

| Mobile item | Needs from you |
|---|---|
| Sanctions call-block | the field name + which read carries it |
| Financial Status | the field + values, when formalised |
| Trial-converted signal | the authoritative "converted" field/value |
| Connecting-screen messages | per-call (comms) vs static config, + the tiers |
| Documents (native) | is it native or web; the order + field API shape |
| Gender | confirm the gateway enum standardises on male/female/other |

None of these block the native apps *today* — they're what we need to build the
new behaviour once the backend/admin side lands.

Thanks,
Mobile team
