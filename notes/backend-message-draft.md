# Draft message to the backend team

Copy-paste ready. Full context in [backend-gaps.md](backend-gaps.md).

---

Hey — we've started the native Android and iOS member apps, porting the API
usage from `member-client`. A few things we need from you to keep moving:

**1. GraphQL gateway URL (blocking us right now)**
`member-client` runs behind a proxy so it just calls `/query` relative — the
real host isn't in the repo anywhere. The native apps have no origin to be
relative to, so we need the absolute URL, ideally for dev / staging / prod.
We've got the comms service already (`https://comms-dev.attorneyshield.io`) and
it's responding fine.

**2. A dev member login**
We have the seeded org/jurisdiction/queue IDs from `config.ts`, but no test
account. Could you send an email + password on `ias_dev` we can sign in with?

**3. Token refresh — does it exist?**
`login` returns a `refreshToken` but nothing in `member-client` ever uses it,
and we can't find a refresh operation. Is there one? This matters more for us
than for web: a browser tab is short-lived, but the app can sit in the
background for days. Without refresh, the only correct behaviour is to kick
someone back to the login screen when the token dies — and this is an app people
open during a police stop, so that's the worst possible moment for it.

**4. Is there a one-time-code sign-in?**
The design reference says members can "sign in with a one-time text code
instead" of a password. We can't see an OTP endpoint, so we're building
email + password for now — just want to confirm we're not missing something.

**5. Heads-up, not a request:** `POST /api/vonage/video/member-call` takes no
auth at the moment. We're not designing around it, just flagging it, since it
means anyone can place a call against any org/member ID they can guess.

**6. When you get a chance:** could we get a window with a dev attorney online?
Right now `member-call` returns `409 no attorney is available` — which is
correct and confirmed the contract works, but it means we haven't been able to
prove a video call actually connects end to end yet.

Separately, and no rush since it blocks a later phase rather than this one —
there are no endpoints yet for the in-app registration screens (phone + SMS
verification, personal details, address, PIN) or for the document vault, family
sub-accounts, activity timeline, or notifications. Are those on the roadmap? We
can't size that phase until we know. (Payment itself isn't a gap — we can see
checkout happens on the web and the app picks up afterwards via a deep link. On
that: we'll need the exact deep-link URL format when it's settled.)

Thanks!
