# Backend — round 2

**To:** mobile (Android + iOS)
**From:** backend
**Date:** 2026-08-14
**Re:** your reply of 2026-08-13
**Environment:** `https://gateway-dev.attorneyshield.io/query` · `https://comms-dev.attorneyshield.io`

Everything you answered is now built. Two of the four were straightforward; the
trial one turned out to be the most interesting thing in either document, and it
found an unrelated bug on the way.

---

## At a glance

| Your item | Status |
|---|---|
| **D1** — you send the header | ✅ **`warn` is off.** dev enforces, same as uat and prod |
| **A4** — `{ id, displayName, isAvailable }` | ✅ **Shipped** — `commsAttorneysForMember`. Two corrections below |
| **Trial** — nothing converts a trial | ✅ **Shipped** — `convertMyTrial`, plus a test member sitting on a trial |
| **B7** — collect only | ✅ Nothing to do. Closed |
| **B5** — guest | ⏸️ With the product owner, framed as you put it |
| **C4** — you fixed the copy | 🙏 Noted below |

---

## 1. D1 — enforcement is on

`COMMS_REST_AUTH_MODE` is gone from the dev manifest, which **is** the enforcing
state: `warn` was the only value that permitted, so removing it closes the door
rather than opening it. Nothing to do on your side.

**Your point about `warn` masking a regression was the better argument for
turning it off, and it is why this happened today rather than next week.** You
were right: a header regression under `warn` would not have failed, it would
have quietly succeeded unauthenticated and surfaced at `uat` as a mystery. That
inverted assertion is now load-bearing — please keep it.

For completeness, the other three clients: member-client shipped it, and
`lfr-desktop` needed a **release**, not just a merge — the fix was on `dev` but
no attorney was running a build that contained it, and enforcing would have
emptied the in-call documents sheet for anyone on 0.5.26. `dev-v0.5.27` is cut
and published for all three platforms, with auto-update. That is why enforcement
landed a few hours after your confirmation rather than immediately.

**On `/api/calls/member-documents`:** understood, you do not call it yet. When
you build screen 30A it is `GET ?callId=<uuid>` and it now checks that the
caller is the member on that call, or staff. Carry the header from the first
line as you said and there is nothing else to it.

---

## 2. A4 — the roster is live, with two corrections

```graphql
query {
  commsAttorneysForMember(jurisdictionId: $jdx, limit: 20) {
    id            # partner_attorneys.id — exactly what member-call takes as attorneyId
    displayName
    isAvailable
  }
}
```

`currentCountry` / `currentSubdivision` are accepted too and take precedence,
mirroring `member-call` — so a travelling member sees the pool they would
actually reach.

Available attorneys sort first, then by name. Attorneys with no display name are
omitted, since the label is the whole control. An empty list is normal and means
"hide the row" — exactly the auto-match fallback you described.

### `isAvailable` is computed by the router itself

This is the part worth reading. Your argument — that offering someone who cannot
answer turns a one-tap connect into a 409 at the worst moment — only holds if
the roster and the router agree, and the obvious way to build this would have
had them drift apart within a month.

So availability is not a parallel rule. It is two passes over the router's own
predicate: relaxed for the roster, and strict (online with fresh presence, under
their concurrent-video cap, covering the jurisdiction) for the flag. The 120s
presence window is now a single shared constant rather than a copy in each
package, and the test asserts the strict pass uses the *router's filter* rather
than asserting an expected list — so if someone later changes how routing picks,
this fails instead of silently lying to your users.

### Correction 1 — the pool is jurisdiction-wide, not the member's partner

You asked for it "scoped to the member's own partner". It is not, deliberately,
and scoping it that way would have shown a roster the router would never honour.

Members are **not** tied to their organization's attorneys. A corporate tenant is
usually not a law firm — a mining company whose staff need legal help reaches the
general pool like anyone else. Dedicated pools exist but are opt-in per queue,
which this first version does not model.

So the row shows who could actually take the call, which is what you wanted, but
the reason it is the right list is different from the reason you expected.

### Correction 2 — `isAvailable` is a snapshot, not a reservation

An attorney can be taken between the roster loading and the member tapping.
**Keep treating a 409 as normal and falling back to auto-match** — this field
narrows that window, it does not close it. Do not turn a 409 into an error
dialog on the strength of this flag.

### Specialty

Not included. It is not a field so much as an ordering rule — "relevance to the
incident type the member picked" needs someone to decide what relevance means,
and I would rather ask than invent a mapping you then build a sort on. Tell me
the rule and it is a small change.

---

## 3. The trial — you found a real gap, and it was deeper than one mutation

You were right on every point: nothing converted a trial. `createPayment`
records a payment a provider already took, `changeMembershipPlan` changes plan,
and a trial otherwise just lapses into its first cycle when the scheduled job
fires. There was no way to say "charge me now".

```graphql
mutation {
  convertMyTrial(organizationID: $org) {
    membership { id status trialEnd currentPeriodEnd }
    invoice { id number totalCents currency }
    status              # active | past_due
    alreadyConverted
  }
}
```

Self-scoped from your token, like `myMembership` — it deliberately does not take
a membership id, because in the shared consumer tenant one would let a member
charge someone else's trial.

**Three things the screen should handle:**

1. **`status: "past_due"` is not a failure.** It means the charge was taken up
   but not settled — a prompted rail like M-Pesa, or a 3DS challenge. Say
   "pending" and wait for the webhook; do not show an error.
2. **`alreadyConverted: true` is success.** The mutation is idempotent, so a
   double tap or a retry after a dropped response does not charge twice. Treat
   it as done.
3. **No card on file is the one error you must handle.** A trial can be *started*
   without a card — deliberately, since a free trial collects nothing — but it
   cannot be *converted* without one. The error names it, and the gate should
   route to card entry rather than surfacing the message raw.

### A test member is sitting on a trial for you

**`tester6@ainnop.com` — 7-day trial, expires 2026-08-20.**

All three dev test members were on active plans, and one live product per
subscriber is enforced, so a trial could not simply be added alongside. I moved
that one and left `munyira851@gmail.com` active, so you can exercise both states
at once instead of trading one for the other.

**The trial is consumed the moment you call `convertMyTrial`.** Ask and I will
re-arm it — it is a one-line fixture and re-running is expected, not a favour.
For a fresh account, `createMembership(trialDays: 7)` is the real path and needs
nothing from me.

### The bug this uncovered

Converting early has to retire the renewal queued for the *original* trial end.
Left alone it fires on the old date, sees a membership whose period now ends a
month out, and renews for the period after that — charging a member a full cycle
early.

The function for that existed. **It had never worked.** It wrote `'canceled'`
into a MySQL ENUM that did not contain it, and an out-of-range write to an ENUM
is *silently coerced to `''`* instead of failing. Four rows on dev were sitting
at `''`.

It happened to behave correctly — the scheduler only leases `status='queued'`,
so a `''` job does not run either — which is exactly why nobody noticed. Writing
the correct value would have quietly created a fifth.

That is the second time this ENUM trap has cost us (the first was
`calls.end_reason`), which is a lint we do not have and should.

None of this touches you. It is here because you asked for one mutation and it
is fair to say what the mutation turned over.

---

## 4. B7 — closed

Nothing to mirror, nothing to build. The Stripe SDK collects the ZIP during
tokenisation, and `attach` → `setDefault` → `detach` is the replace-card flow.

Thank you for taking 33D back to design rather than asking us to fake an
inline edit — "we would rather change the screen than pretend" is the right
instinct and it saved a field we would have had to keep in sync forever.

---

## 5. B5 — with the product owner

Framed as you put it: two independent reasons the entry point cannot work as
drawn, either fatal on its own. Nothing is being built until it comes back.

The trial half is now unblocked independently of the guest question — so V2 and
T5–T8 are yours whenever you want them, and only the G-screens wait on the
decision.

---

## 6. C4 — thank you for changing that copy

You did not have to tell us you had shipped it, and the fact that you did is why
this is worth saying: an app promising people that someone will be alerted with
their location during a police encounter, when nothing sends it, is the worst
kind of bug — invisible, and it fails exactly when someone is relying on it.

Fixing the code comment that carried the same false rationale is the detail that
matters most. A wrong reason left in place is how a corrected behaviour drifts
back.

**Nothing has changed on our side yet: the alert is still unbuilt and still has
no owner.** It is escalated. I will tell you when it moves, and until then your
smaller promise is the honest one.

---

## Still open

| | |
|---|---|
| **Emergency-contact alert (C4)** | Unbuilt, no owner. Escalated |
| **Guest model (B5)** | With the product owner |
| **Transcripts (B6)** | Not scheduled |
| **`image` field type (A6)** | Stays unmapped until the templates are cleaned |
| **Specialty ordering** | Tell me the relevance rule |
| **E2 domain files** | Waiting on your fingerprint + Team ID |

Nothing here blocks you. Everything you queued in your reply — B3, A5, A8, B8,
B1, B2, B4, C8, C2 — is live on dev and behaving.
