# Backend follow-ups for Innocent — 2026-09-08 (mobile)

Three items: one blocker needing a definitive answer, one open question, one FYI.

## 1. Deep-link domain — we need one definitive answer (BLOCKER)

Your two answers contradict each other and we can't wire the app until it's settled:

- **E1** said the contract is ours as-built: `/app/return`, `/return-to-app`, `/app`
  on **`attorney-shield.com`**, "no change needed."
- **"Answers for round two"** said the opposite: `attorney-shield.com` "appears in
  our config only as the Mailgun sending domain … nothing in Terraform or the
  cluster serves it," that **none of our three paths is in use**, and offered to
  host `/.well-known/` per-environment on **`attorneyshield.io`** with a return URL
  of **`/app/return?email=<urlencoded>`**.

**What we need from you (pick one, definitively):**
1. Which host will actually serve `/.well-known/apple-app-site-association` and
   `assetlinks.json` — `attorney-shield.com` or `attorneyshield.io`? (Per env if
   they differ.)
2. The exact post-checkout return path + query (e.g. `/app/return?email=…`).

The moment we have that, we point the iOS Associated Domains + Android intent
filter + both `DeepLinkParser`s at it. The association-file values are ready and
public by design (in `asi-claude/notes/wellknown/`): Team ID `TWKX78WDP7`, package
`com.app.attorney.shield`, both signing SHA-256 fingerprints — hand them to devops
for whichever host you confirm.

## 2. Additional-seat `seatPriceId` — where does the client get it? (QUESTION)

Round-two confirmed included seats work and that the `Entitlement` carries the seat
fields, but there is **no `seatPriceId`**. For a member buying a *paid* additional
family seat, the app needs a price identifier to start checkout. Where should the
client source it — a field on the plan/catalogue, a new entitlement field, or a
fixed per-org price? Until we know, paid additional seats can't be wired.

## 3. FYI — mobile now shares your login contract (no ask)

Both mobile apps now use the same sign-in contract member-client drives, so nothing
should surprise you:
- `verifyLoginOtp(origin: APP, firstName, lastName)` — we send the guest's name on
  the guest-door path; you already stamp the display name only on a new account.
- `requestLoginOtp { … passwordSignInAvailable }` — we request it and **retry
  without the field** if the gateway hasn't introspected it yet, so a federated
  lag never breaks our login screen.

No backend change requested — just confirming we're on the same contract.
