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

## Not done

- Live reproduction: the emulator was signed out ("signed in on another device"),
  and the trial account can't be authenticated here (passwordless email code /
  unknown password; single-device would kick the user's session). Awaiting the
  on-screen error text or a logcat capture (`adb logcat -s AsiTrial:* AsiApi:*`).
