# 2026-08-14 — Trust the member's own org; stop seeding jurisdiction

## Task

The backend traced a live bug in the web member client and told us both native
apps — ports of that code — have it. Their write-up
(`2026-08-14c-member-context-dev-defaults.md`) was precise; this is the fix.

**The bug:** a case's organization outranked the member's **own** record in
`SessionManager`. Because a case is created with whatever org the app is
carrying, one transient `getMe` failure fell back to the dev **seed** org,
stamped it onto a new case, and every later launch read it back **from that
case** — a single blip became permanent, and everything money-related
(entitlement, membership, saved cards, payment profile) was filed under the
wrong org. On dev, 16 of one member's cases were stamped with the seed org
before the backend caught it.

## The five items, and what I did

| # | Item | Action |
|---|---|---|
| 1 | Case org outranked the member's own | **Fixed** — precedence + re-resolve on restore |
| 2 | Seed jurisdiction substituted when a case names none | **Fixed** — nullable, no default, omitted from the call |
| 3 | Dev queue / partner ids on member paths | **Removed** the queue seed; partner was never defaulted |
| 4 | Neither app sends current location | Noted — optional travel-routing feature, not done |
| 5 | `member-call` sent no `Authorization` | **Already done** (D1, earlier) — verified the bearer is attached |

### 1. Organization precedence

`adopt()` now resolves org as **member's own record → case → previous → seed**,
holding the whole `Me` rather than folding it into a var. A case's org is a
fallback, never the source of truth.

And `restore()` no longer just loads and stops. A new **`refreshContext()`**
re-reads the member's own record once at startup, off the critical path, and
prefers it — so a session that *already* stored a bad org **heals** on the next
launch instead of persisting until sign-out (which a member has no reason to
do). It never clobbers a good value with a blank read: only a successful lookup
with a real org replaces what's there.

### 2. Jurisdiction

`MemberContext.jurisdictionId` and `StartCallArgs.jurisdictionId` are now
**nullable**, with **no seed default**. `member-call` omits the field when it's
null, and comms resolves the routing jurisdiction itself — the member's current
location, then their profile country. Substituting the seed had been stamping a
fictional jurisdiction onto real calls, rooms and cases.

The backend also made this field optional server-side and now resolves from the
profile country, so **routing already improved before we changed a line** — our
calls stopped routing on the seed id the moment they deployed.

### 3. Dev seed cleanup

Deleted `devDefaults.jurisdictionId` and `devDefaults.queueId`. Kept
`organizationId` as the last-resort fallback only (the backend's own suggested
chain keeps it there). `partnerId` was already only ever read from the case —
never defaulted — so nothing to remove.

## The rule, taken to heart

The backend put it well: *a seed id substituted for a real member is not a
fallback, it is a silent misroute.* Anything the server can derive itself will
eventually arrive wrong, so we now send nothing and let it answer. I checked for
other `devDefaults.*` on member paths — only `organizationId` remains, and only
as the final fallback the backend's own code keeps.

## Files

- **kotlin**: `SessionManager.kt` (precedence + `refreshContext`), `MemberContext.kt`
  (nullable jurisdiction), `Models.kt` (`StartCallArgs`), `AsiApi.kt` (conditional
  body), `AsiConfig.kt` (`DevDefaults` trimmed), `MainActivity.kt` (call
  `refreshContext` once at startup).
- **swift**: the same shape — `SessionManager.swift`, `MemberContext.swift`,
  `Models.swift`, `AsiApi.swift`, `AsiConfig.swift`, `AttorneyShieldApp.swift`.

## Tests

**Android 427 / 0**, **iOS 405 / 0** — 3 new each: own-org precedence over a
case, `refreshContext` healing a stored wrong org, `refreshContext` not
clobbering a good org on a failed read, and the call omitting an unknown
jurisdiction.

## Verification against the backend's steps

- The unit tests assert the core invariant: after sign-in, org = the member's
  own `user.organizationID`, not the case org.
- Still **to do live** (their step 1): sign in on a device, confirm
  `session.organizationId == user.organizationID`, place a call, relaunch, and
  confirm it **stays** equal — the loop that used to break. Worth running on the
  real Infinix device next session.

## Open issues / next steps

- **Item 4 (current location)** — optional but genuinely useful: a member
  arrested two states from home currently reaches an attorney licensed where they
  *live*, not where they *are*. The contract is `currentCountry` /
  `currentSubdivision` (home from profile, current from device timezone — never
  locale). Worth doing as a follow-up.
- **Live org-heal verification** on a real device, per the backend's step 1.

---

## Live org-heal verification (Infinix X6886) — done

Ran the backend's step 1 on the real Android phone, with a temporary
`ASI-CTX` debug log in `adopt`/`refreshContext` (added, read, then **reverted**
— not committed):

**Sign-in:**
```
adopt org=6c53e00d… jur=de400000… (me=6c53e00d… case=6c53e00d…)
```
Session org = the member's **own** record = `user.organizationID` (`6c53e00d`),
read from `me`, exactly the invariant.

**Relaunch:**
```
refreshContext org=6c53e00d… (was=6c53e00d… me=6c53e00d…)
```
`restore()` loaded the session and `refreshContext()` re-resolved — the org
**stayed** `6c53e00d`. The "must stay equal after relaunch" half holds.

What I could not stage live: a case org that *differs* from the own org, to
watch the heal flip a wrong value — this member's data no longer diverges
(their cases are already `6c53e00d`). That exact flip is covered by the unit
test (`refreshContext heals a stored wrong org`), and the live log proves
`refreshContext` reads `me` and prefers it, so the two together are conclusive.

Observability note for next time: the session is `EncryptedSharedPreferences`
(not readable off-device), the app has no org logging, and comms now overrides
the case org from the JWT — so the resolved org can only be observed live via a
temporary debug log, which is what this used.
