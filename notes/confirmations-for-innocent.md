# Confirmations back to Innocent — re: "Six Asks From Mobile"

**From:** Mobile team · 2026-08-31

Thanks — this is exactly what we needed. Answers to your open questions, plus two
small things from #5.

## #1 Sanctions — field name: yes to `myAccountRestriction`

Confirmed: **`myAccountRestriction` returning a nullable reason**, not a bare
boolean. Your reasoning is right — the member is entitled to be told *something*,
the message differs by reason, and a nullable-reason field grows a second block
type later without a schema change. Self-scoped from the token, as you describe.

On the app side we'll gate on it **ahead of** the trial/guest/expired checks
(sanctions overrides all of them): non-null reason → disable the connect button
and show the reason (falling back to "Support is paused on your account — contact
support." if the reason is empty).

## #2 Financial Status — field name: yes to `myFinancialStatus`

Confirmed: **`myFinancialStatus`**, same `MemberStatusRef` shape as
`myAccountStatus`. We'll key on it directly once it's readable and stop inferring
from `entitled` + `graceUntil` — noted especially that **canceled ≠ expired**,
which the inference can't separate today.

Ship #1 and #2 together whenever ready; we'll wire both as soon as they're on dev.

## #3 — thanks, no change needed

Keeping `membership.statusCode != "trial"`. We've already shipped the
`failureReason` handling: a `failed` conversion now shows the decline reason on
the charge notice instead of a generic error, and no longer polls as pending.
We'll pick up `membershipEntitlement.conversionPending` for the cold-start case
when we next touch the trial cold-load.

## #5 Documents — mostly already wired; two things

Good news: the native apps **already** render admin document types, fields, the
three new fields (state_of_issue / gun_owner as dropdowns, health_conditions as
text), their `options` (we handle both the JSON-string and array shapes), and both
`sortOrder` levels — and we do **not** swallow a failed load as empty config. So
that half is done on our side.

Two points before we call #5 closed:

1. **Icons — a decision, not a bug.** We currently draw a curated local glyph per
   document type (keyed on its `code`), and deliberately ignore the admin `icon`
   field — because on dev those values are unreliable (a mix of CloudFront URLs
   and the literal string `"globe"`), so honouring them would show broken/placeholder
   marks and a raw uploaded image also clashes with the app's vector icon set.
   **Question:** do you want the app to render the admin-uploaded `icon` URL
   (we'd add a remote-image path with a fallback to the local glyph), or keep the
   curated local glyphs? If the former, we need the admin icons to be real, sized
   images rather than placeholders.

2. **Country scoping.** member-client calls `adminDocumentFieldList` with
   `countryISO2`. Our two queries (`adminDocumentTypeList` + per-type
   `adminDocumentFieldList`) don't pass a country today. **Question:** with no
   `countryISO2`, does the resolver return *all* active types (global +
   country-specific) or only the global ones? If country-specific types are
   dropped without it, that would explain the "some active types don't appear"
   note — tell us and we'll pass the member's country (we have it from the device
   region / profile).

## #4 — over to David

Agreed on static admin config `[{ afterSeconds, message }]`, fetched + cached,
with our hardcoded fallback. We'll build the read once we have the three strings
and the master table.
