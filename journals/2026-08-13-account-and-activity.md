# 2026-08-13 — Activity and the account section (screens 32, 33, 33A–33C)

## Task

Build the next screens, and re-check the backend after "I'm done with my end".

## Outcome

**Built on both platforms and verified against dev.**

| Screen | Status |
|---|---|
| 32 — Activity · timeline | Built |
| 33 — Profile · account | Built |
| 33A — Payment & plan | Built |
| 33B — Family members | Built |
| 33C — Settings | Built |
| 33D — Payment method · view & edit | **Not built** — no write path exists (B7) |

The four-tab bar (Home / Glovebox / Activity / Profile) arrived with them.

---

## First: what the backend actually shipped

The message was "done with my end". Re-ran every item in
`notes/backend-asks.md` against dev rather than taking it at face value:

| Checked | Result |
|---|---|
| `countries` | **Fixed** — returns United States, was `[]` |
| Schema shape | **Byte-identical**: 238 queries, 297 mutations, no type or input-field changes |
| A5 `deleteUserDocument` | still `forbidden` |
| A6 `type` vocabulary, dev test rows | unchanged |
| D1 unauthenticated `member-call` | still accepted |
| A4 `casesByUser` | not empty — **but only because our own test calls made six cases**. `partnerID` null, jurisdiction still the hard-coded dev seed, `partnerAttorneys` still `[]` |

So exactly one thing landed: the countries fix he had said he was working on.
B1–B5 could not have moved — the schema is unchanged to the byte.

**The bigger finding was ours, not theirs.** We had never looked past
registration. When we did, most of the account section already existed:
`myMembership`, `membershipEntitlement`, `myPaymentMethods`, `mySubaccounts`,
`addSubaccount`, `removeSubaccount`, `sendUserInvite`, `invoicesBySubscriber`,
`commsCallsByMember`, `changePassword`, `adminTermsOfService`, `deleteMyAccount`.
Five screens' worth of backend we had been assuming was missing.

---

## The data is real

| | |
|---|---|
| Plan | Freedom Basic — Family, $38.00/mo |
| Seats | Freedom Basic — Family Additional Seat × 2, $8.00/mo |
| Total | **$46.00/mo** — matches invoice `INV-202608-0876900d`, Paid |
| Renews | Sep 13, 2026 |
| Card | Visa •••• 4242, expires 11/42 |
| Sessions | six real calls, two of them unanswered |
| Legal | four published documents |

---

## Decisions

**The plan name is a rule, not a field.** `Membership.packageID` is null and
nothing else names the plan, so the plan is **the dearest line** — a seat costs
less than the plan it extends. Chosen over matching `"Seat"` in the product name
so it survives a rename or a translation.

**Line items, not one number.** The membership genuinely is a plan plus paid
seats. Collapsing them to "$46.00/mo" would hide what the member is charged for.

**Coverage comes from the entitlement, never the membership status.** A
membership row can read `active` while entitlement has lapsed to grace. This card
is where a member checks whether they are protected, so it follows `entitled`.
Pinned by a test that sets one to `active` and the other to `false`.

**A call nobody answered gets no duration.** `no_answer` calls still carry a
start and an end; rendering "1m 04s" against one would read as a one-minute
consultation that never happened. Only connected calls show a length.

**The join event is pinned, not sorted.** It is the timeline's origin, and a
backfilled or skewed `createdAt` must not float "You joined Attorney Shield" into
the middle of someone's sessions.

**Delete account is behind a typed confirmation.** `deleteMyAccount` takes no
arguments and cannot be undone. It is also rendered as a plain outlined control
rather than in red — the palette has no approved danger colour and forbids
inventing one (`color-system.md` §6), which is the same interim rule the hang-up
button already follows.

**Legal text is converted once, in shared code.** Android could render the HTML
with `AnnotatedString.fromHtml`, but the iOS equivalent builds an
`NSAttributedString` carrying its own fonts and colours — which would fight the
palette — and is slow on documents this long.

**The tab bar arrived now** because until Activity and Profile existed it would
have been a bar with two live tabs and two that went nowhere. It owns the bottom
window inset; the four screens above it pad only their top and sides.

---

## Three things a test or a screen caught

### 1. The wrong id, silently accepted

`seatPriceId` returned the membership **item** id (`i-seat`) rather than the
**price** id (`p-seat`). A test caught it.

This one mattered because of A7: the gateway does **not** validate `seatPriceID`.
We proved that by accident — sending an all-zeros UUID created a real
sub-account. So the wrong id would not have failed; it would have created a
family seat billing against nothing. `MembershipLine` now carries both ids with a
comment saying why.

The probe sub-account was removed immediately (`removeSubaccount` → `true`,
`mySubaccounts` → `[]`, seats back to 1).

### 2. Raw HTML on screen

The Legal viewer rendered `<p><strong>Attorney Shield Terms of
Service</strong></p>` with the tags showing. Every unit test passed. Visible only
by looking at a device — the same lesson the Glovebox's `image` field taught.

### 3. An hour lost to the wrong app

Sign-in kept failing with `Unknown type "LoginInput"` while the same mutation
worked from curl. The build has an `applicationIdSuffix` of `.debug`, so
`adb shell am start -n com.app.attorney.shield/...` was launching **yesterday's**
APK, still installed under the un-suffixed id. `installDebug` had been reporting
success the whole time, for a different package.

Worth remembering: `adb shell pm list packages | grep attorney` before believing
any on-device symptom.

---

## Files touched

**`kotlin`** — `core/format/` (new: `Formats.kt`, `Html.kt`),
`core/network/AccountModels.kt` (new), `core/network/AsiApi.kt` (16 operations),
`feature/activity/` (new), `feature/account/` (new),
`core/design/AsiComponents.kt` (`AsiNavRow`, `AsiGroupHeading`, `AsiTabBar`),
`MainActivity.kt` (two destinations + the tab scaffold), and the inset change on
Home and Glovebox.

**`swift`** — the same structure: `Core/Format/`, `Core/Network/AccountModels.swift`,
`Core/Network/AsiApi.swift`, `Feature/Activity/`, `Feature/Account/`,
`Core/Design/AsiComponents.swift`, `AttorneyShieldApp.swift`.

---

## Test results

| Suite | Result |
|---|---|
| Android unit | **283 pass**, 0 fail (was 226) |
| iOS unit | **279 pass**, 0 fail (was 221) |
| iOS UI | **3 fail — pre-existing**, see below |

Coverage: money/date/duration formatting with a pinned time zone, HTML
conversion including double-escaped entities, plan-name and total derivation,
entitlement-over-status, grace vs lapsed, seat maths and the floor at zero, the
seat-price rule, invite/remove/resend, password validation, forms cleared on
leaving, and that no destructive call is made without the typed confirmation.

**The three `DynamicTypeUITests` failures are not from this work** — they fail
identically on the unchanged tree. They assert the Welcome screen, and the
simulator has a restored session, so the app opens on Home. The tests are
environment-dependent; they need to clear the keychain before launching.

### Verified on device against gateway-dev

**Android** — Activity with all six sessions, "No attorney answered" carrying no
duration, Profile with the real plan, Payment & plan with both line items and the
$46 total, Billing history with the paid invoice, Family members at "0 of 2",
Settings, and the four legal documents rendering as readable text.

**iOS** — the same screens, the same numbers, the same text.

---

## Open issues / next steps

1. **Screen 33D is not built.** No `updatePaymentMethod`, no billing-ZIP field,
   and `attachPaymentMethod` wants a provider token the app cannot mint. Raised
   as B7 with three options in preference order.
2. **No attorney names on the timeline.** The nested resolver 504s after 60s
   (A8), and `attorneyId` has no member-callable lookup.
3. **No "View transcript"** on Test Call rows — nothing matching `transcript`
   exists (B6).
4. **Push notification settings (screen 26) are not built.** The profile carries
   `notificationsEnabled` and `marketingOptIn`, and `notificationList` /
   `markNotificationRead` exist, so screens 22–26 are buildable — just not built.
5. **Language is not switchable.** `primaryLanguageTag` is writable and there are
   three languages seeded; the app is English-only for now.
6. **The iOS UI tests need fixing** so they do not depend on a signed-out
   simulator.
