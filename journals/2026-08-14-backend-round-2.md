# 2026-08-14 — Closing A5, A8 and A4

## Task

Act on the backend's round-2 response.

## Outcome

**Three asks closed on both platforms.** Everything they shipped that we had
queued is now built, except the trial screens — which are unblocked but cannot
be *verified* yet (see below).

| Ask | What shipped here |
|---|---|
| **A5** | The `✕` on every document tile, with a confirm |
| **A8** | Attorney names on the Activity timeline |
| **A4** | The roster moved to `commsAttorneysForMember` |

Plus: the two probe files stuck on the test account since the Glovebox was built
are finally deleted.

---

## A5 — the delete control

Left out of the original Glovebox with a recorded reason: `deleteUserDocument`
returned `forbidden` for a member's own file, and a control that always fails is
worse than none. It now authorizes against the document's owner.

**Confirmed rather than immediate.** The bytes go with the row, so there is
nothing to undo *to* — which is why this asks first instead of offering an undo
afterwards. Rendered as a plain outlined action, not red, per the palette's
standing rule.

---

## A8 — attorney names, via the flat field

The backend did not fix the nested resolver, and explained why: `PartnerAttorney`
in comms is a federation reference stub, so `attorney { displayName }` is a
cross-subgraph hop that hangs. They added `attorneyDisplayName`, read locally.

**A test asserts we ask for the flat field and not the nested one.** The nested
selection still exists for the desktop app and still 504s, so this is a trap that
stays available to anyone editing the query.

**The attorney who accepted, not the ones who were tried.** A call carries one
assignment per attorney the router offered it to; naming a `timeout` assignment
would credit the wrong person.

---

## A4 — and a correction worth recording

We asked for the roster "scoped to the member's own partner". **That was wrong,
and the backend was right to refuse it.**

Members are not tied to their organisation's attorneys — a corporate tenant is
usually not a law firm, so its staff reach the general pool like anyone else. A
partner-scoped roster would have listed people the router would never route to:
a list that looks right and produces a `409` on every tap.

So the pool is jurisdiction-wide, and our `listAttorneys(partnerId)` became
`listAttorneys(jurisdictionId)`.

**`isAvailable` is a snapshot, not a reservation.** Someone can be taken between
the roster loading and the member tapping. A `409` therefore stays a normal,
retryable outcome that falls back to auto-match — this narrows the window, it
does not close it. That is written on the model rather than only in the doc,
because the model is where the next person will look.

They also built the flag out of the router's own predicate rather than a parallel
rule, so the roster and the routing cannot drift apart. Verified live: seven real
attorneys, all currently `isAvailable: false` because nobody is online in the
desktop app.

---

## A process note: I was reading stale test results

Three roster tests kept failing identically across several fixes. The cause was
that **the test compile was failing**, so the task never reran and I was reading
the previous build's XML each time.

`--rerun-tasks` does not help when compilation is what broke. The fix is to check
`compileDebugUnitTestKotlin` output before trusting a result file — a failing
suite and a stale suite look identical from the outside.

---

## Test results

| Suite | Result |
|---|---|
| Android unit | **342 pass**, 0 fail |
| iOS unit | **323 pass**, 0 fail |

---

## Open issues / next steps

1. **The trial screens are unblocked but unverifiable.** `convertMyTrial` shipped
   and a trial member exists (`tester6@ainnop.com`, expires 2026-08-20) — but we
   have no password for it and OTP needs that mailbox. **We need credentials, or
   a trial on an account we can already reach.**
2. **`convertMyTrial` charges a card and consumes the trial.** It will not be
   called speculatively; only deliberately, once, when the screens exist.
3. Still queued from round 1: **B8** (the rest of screen 26), **B1** (screens 08
   and 09, six digits), **B2** (pronouns), **B4** (notify-by), **C8** (the
   onboarding flag), **C2** (token refresh through one shared in-flight promise).
4. With the product owner / David: the emergency-contact alert, the guest model,
   and the specialty ordering rule.
