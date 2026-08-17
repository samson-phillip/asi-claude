# 2026-08-17 — Register button: UAT, and where the URL lives

## The report

Tapping **Register** opened `https://attorney-shield.com` — production — from a
build pointed at dev everywhere else.

## Was a UAT URL ever supplied? No

Checked rather than recalled. Every host ever given to us:

| Host | Where it came from |
|---|---|
| `https://gateway-dev.attorneyshield.io/query` | `lfr-desktop/.env.example` |
| `https://comms-dev.attorneyshield.io` | same |

`https://attorney-shield.com` was **a placeholder I chose**, recorded as such in
both call sites and in backend-gaps §6 ("the marketing host until confirmed").
Nothing for registration or checkout had ever been supplied, for any
environment. Now it has: `https://uat.attorney-shield.net/choose-plans`.

**Note the TLD.** Registration is on attorney-shield **.net**; the `.com` the app
was opening is the marketing site. Easy to misread as a typo — it is not.

## The structural fault behind it

The URL was a constant in `MainActivity` / `AttorneyShieldApp`, *outside*
`AsiConfig`, while every other host lives inside it. So it could not follow the
environment the build was made for — a dev build necessarily sent members to
production. It now sits beside `graphqlUrl` and `apiBaseUrl`.

Defaulted rather than required: eight test files construct an `AsiConfig` and
have no interest in checkout.

## member-client is no help here

Asked whether the reference app shows how Register should work. **It has no
Register button.** Three screens (`LoginScreen`, `HomeScreen`, `CallScreen`), a
login that is email + password only, and an `api.ts` carrying `login()` and no
OTP operations at all. No external links anywhere in `src/`. It assumes a member
who already has an account and a password, so there is nothing to copy.

That is worth holding on to: **`member-client` cannot be the behavioural
reference for registration**, only for sign-in, home and the call.

## A consequence that needs a decision

Registration now happens on `uat.attorney-shield.net`. The hand-off *out* works.
The hand-back does not:

- Android `AndroidManifest.xml` declares intent filters for
  `attorney-shield.com` and `www.attorney-shield.com` only.
- `DeepLink.ALLOWED_HOSTS` is the same pair, and refuses anything else by
  design.
- E2's `assetlinks.json` / AASA notes cover the same two `.com` hosts.

So a return deep link from UAT checkout (development plan §3, screen 08) will
not open the app. Either UAT needs its own association files and an added host,
or the return leg is only ever testable against production. **Not changed
here** — widening the deep-link allow-list is a security decision, and the
allow-list refusing unknown hosts is currently doing exactly what it was written
to do.

## Tests

| Suite | Result |
|---|---|
| Android unit | **433 / 433**, 0 failed |
| Android instrumented | **30 / 30**, 0 failed |
| iOS unit | **421 / 421**, 0 failed |

## Open

- Does the **rebuilt** registration flow keep the `/choose-plans` path? The URL
  supplied is the old app's.
- Deep-link return from UAT (above).
