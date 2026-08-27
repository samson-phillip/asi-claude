# 2026-08-27 — Trial won't convert: diagnosis + logging

## Symptom

A trial account (`x1@jahbroicl.com`) reaches the V2 gate (trial detection works),
taps "Start Membership to Connect Live" → "Yes, charge my card", and **the account
does not convert**. Checking logs showed nothing.

## Diagnosis — the request is correct; the server rejects it at runtime

Verified `convertMyTrial` directly against `gateway-dev`:

- **Introspection:** every field the app selects exists — `ConvertTrialPayload`
  has `membership: Membership!`, `invoice: Invoice`, `status`, `alreadyConverted`;
  `Invoice.id` and all the `Membership`/items/price/product sub-fields exist too.
- **Probe:** sending the app's *exact* mutation unauthenticated returns
  `"unauthorized"`, **not** a "cannot query field" validation error — proving the
  query is schema-valid. A client query bug would have surfaced here.

So the conversion is a **runtime rejection** from the backend for this trial
account. The app already surfaces the reason on the charge notice (`error`), but
logged **nothing** — hence the empty logs.

Leading cause: **no default payment method on file** (the app's own
`TrialViewModelTest` covers "no card on file surfaces the reason on the notice").

## Fix (this task)

Added logging so the real reason is captured (`kotlin` + `swift`):

- `AsiApi` — log every GraphQL error and malformed response with the operation
  (`GraphQL error · mutation ConvertMyTrial · <reason>`).
- `TrialViewModel` — log the convert attempt and outcome (`convertMyTrial failed
  · <reason>` / `ok · status=…`).
- `kotlin` `build.gradle.kts` — `unitTests.isReturnDefaultValues = true` so
  `android.util.Log` in these paths is a no-op in JVM tests, not "not mocked".

Android suite green; iOS build green. Kotlin logging build installed on the
emulator. Shipped: `kotlin@dev bff8051`, `swift@main 54bde1c`.

## Product gap to raise (likely, pending confirmation of the reason)

If the reason is "no card on file": the app has **no in-app add-card** (screen
33D not built — `attachPaymentMethod` needs a provider token the app can't mint,
`notes/backend-asks.md` B7). So a trial created **without** a card cannot be
converted in-app at all today — a real gap, not just a bug. Depends on whether
the web trial signup captures a card; needs product/backend confirmation.

## Resolution — the log (2026-08-27, from the user's device)

```
AsiTrial  convertMyTrial → org=6c53e00d-…
AsiTrial  convertMyTrial ok · status=past_due  alreadyConverted=false
          membership=trial  invoice=f651b7c0-…
```

The request works — it raises an invoice and returns cleanly. The result is
**`status=past_due`, not `active`**: the charge is taken up but not settled to
paid. Two separate problems:

1. **App bug (fixed).** `TrialViewModel` treated *any* successful return as
   `Confirmed` ("You're covered"), ignoring `status` — so a `past_due` result
   showed the T8 success receipt while the account stayed unpaid. That is what
   read as "it doesn't convert". Fixed to mirror member-client's
   `stepForConversion`:
   - `active` / `alreadyConverted` → `Confirmed`
   - `past_due` → **new `Pending` step** ("Payment pending… activates when it
     clears"), which never claims coverage
   - anything else → back to the notice with a reason

   Both apps + tests (`past_due → Pending`, unknown → not-covered). Shipped:
   `kotlin@dev 87c94d9`, `swift@main 546dc63`.

2. **Why `past_due` (payment side, not the app).** The charge lands unpaid —
   most likely the card on `x1@…` is declining/absent on dev, or Stripe needs an
   action it isn't getting. The app can't fix this; check the payment method on
   that account / with backend. After a `past_due` convert, Home now correctly
   shows the "couldn't process your payment" state (account-gating work), rather
   than pretending coverage. Structural limit to flag: no in-app add/replace
   card, so a trial with no usable card can't be settled from inside the app —
   a product/backend gap (`notes/backend-asks.md` B7).
