# 2026-08-31 — Deep-link domain: keep `attorney-shield.com` (do NOT switch to .io)

## Decision

**No code change.** The post-registration deep-link domain stays
`attorney-shield.com` / `www.attorney-shield.com`. An earlier batch plan said
"switch the domain to `attorneyshield.io`" — that is **wrong**, and this entry
records why so it isn't revisited.

## Why the earlier plan was wrong

`attorneyshield.io` is the **backend infrastructure** domain — `gateway-*`,
`comms-*`, `member-client-*.attorneyshield.io`. The deep link is the **web→app
handoff after checkout**, and checkout happens on the **Webflow marketing site**,
`attorney-shield.com` (every web-chrome frame in the CodePen shows
`attorney-shield.com`). The two are unrelated; pointing App Links at the infra
domain would point them at a host that never serves the checkout-return page.

Innocent settled this explicitly (backend response, **E1**):

> "your implementation is the contract. `/app/return`, `/return-to-app` and
> `/app` on `attorney-shield.com` and `www.attorney-shield.com`, carrying `email`
> and nothing else. **No change needed.**"

## Audit — both platforms already match the confirmed contract

- **Hosts:** `attorney-shield.com`, `www.attorney-shield.com` (exact; subdomains
  not implied). Swift `DeepLinkParser.allowedHosts`, Kotlin
  `DeepLinkParser.ALLOWED_HOSTS`.
- **Paths:** `/app/return`, `/return-to-app`, `/app` (exact match, authority in
  the parser). Swift `returnPaths`, Kotlin `RETURN_PATHS`.
- **https-only**, **email is a prefill only** (link carries no authority; a token
  in the query yields nothing — there's a test asserting that).
- **Android intent-filter** (`autoVerify=true`): `pathPrefix="/app"` covers `/app`
  and `/app/return`; `pathPrefix="/return-to-app"` covers the third. Both hosts.
  The parser remains the authority (an intent-filter can't express "https only on
  these exact hosts"), so a stray `/application` link opens the app but the parser
  rejects it.
- **Custom-scheme fallback** (`attorneyshield://return?email=…`) for the manual
  "Open app" path on screens 07/T4.

So there is nothing to change in `kotlin`/`swift` for #9.

## What actually remains: E2 (devops, not app)

The only open deep-link item is **E2 — host the association files** so the
web→app open is silent (no Android disambiguation dialog, iOS Universal Links).
Innocent's status: *"Waiting on your fingerprint + Team ID."* Those values —
and the ready-to-host files — already exist in `notes/wellknown/`:

- `apple-app-site-association` — Team ID `TWKX78WDP7`, appID
  `TWKX78WDP7.com.app.attorney.shield`, the three paths.
- `assetlinks.json` — package `com.app.attorney.shield`, **both** real signing
  SHA-256 fingerprints (`46:52:…:ED:AA` app-signing/key1, `FF:B0:…:7E:16` upload).

These are **public by design** (served at `/.well-known/`), so the fingerprints +
Team ID go straight into the reply to Innocent / the shared artifact — that's the
handoff he's been waiting for. Hosting rules: served from **both** hosts at
`/.well-known/`; AASA as `application/json` with **no `.json` extension** and **no
redirect**.

Separate security note (already in `notes/e2-domain-association.md`, not part of
this handoff): the extracted keystores had weak passwords — recommend rotating
the upload key. That concerns the private keys, never the public fingerprints
above.

## Files

None changed. Verification only, plus this decision record. The E2 values are
carried to Innocent via the shared artifact (see the artifact-refresh entry).
