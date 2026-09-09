# 2026-09-09 — member-client UI-parity audit (branch `mirror-member-client-ui`)

CEO directive via Innocent: drop CodePen as the app blueprint and mirror
member-client (now re-skinned to navy/gold). Design authority updated in CLAUDE.md
(member-client Rank 2 visual+behavioural; CodePen Rank 3 = the *look* of elements
that exist in both, since those frames are better-designed; colour PDF Rank 1).

Phase 1 = audit. Six parallel Explore agents compared member-client → our
kotlin+swift, one per section. **Caveat: this is a code-structural audit — agents
read code, not pixels — so it's a prioritised CANDIDATE backlog to confirm on
device during execution, not gospel.** Headline: the apps are already ~90% there
(same palette, most divergences are polish); the real work is a handful of gaps +
one structural question.

## A. Functional gaps — build (verify first)

| # | Item | Platforms | Impact | Note |
|---|------|-----------|--------|------|
| A1 | **Change / recover PIN in Account** (member-client `ChangePinScreen`) | both | HIGH | We set a PIN in setup but never expose change/recover in Account. |
| A2 | **Theme / Appearance selector** (System/Light/Dark) in Settings | both | MED | The theme *system* exists (AsiColors light+dark); no user control. Confirm app isn't intentionally dark-only. |
| A3 | **Support screen/row** in Account (email + "phone: coming soon") | both | MED | We only surface the support email inside Profile help text. |
| A4 | **TravelPrompt** — cross-border "you appear to be in X" modal | both | MED | Location provider exists; the prompt doesn't. |
| A5 | **IntroVideo screen** (member-client-specific onboarding video) | both | LOW | Not in CodePen; member-client-only. |
| A6 | **"Licensed Attorney Connected"** transient banner on call connect | both | MED | Verify present; member-client fades it after ~4s. |

## B. Structural / layout convergence — change our apps → member-client

| # | Item | Platforms | Impact | Note |
|---|------|-----------|--------|------|
| B1 | **Money onto one screen** — member-client (and CodePen 33A) put plan+payment+family+billing on one "Payment & plan" screen; we split into Plan/Payment/Family/Receipts panes | both | HIGH | Biggest change; needs a design decision before doing. |
| B2 | **Profile name = two-column First/Last row** (we stack them) | both | MED | member-client + CodePen both group them side by side. |
| B3 | **Document viewer = overlay + swipe-down dismiss** (we use full modal / iOS QuickLook) | both | MED | iOS QuickLook is the native idiom — debatable whether to change. |
| B4 | **Family "Invite sent / Resend" on one row** (we put Resend on a separate action row) | both | LOW | |

## C. Already correct per the CodePen rule — KEEP (do NOT "fix" toward member-client)

- Custom PIN keypad (matches CodePen; member-client uses a plain input).
- "EMERGENCY CONTACTS" gold eyebrow (matches CodePen; member-client omits).
- Call "connecting" tips — we correctly dropped the false "contacts alerted with your location" line (backend sends nothing).
- Plan card "You + N members" inline (matches CodePen 33A).
- Granular notification prefs — we already have them (audit false positive).
- Split dialling-code + number phone field (matches CodePen 08).

## D. Low polish — batch

- Copy: Skip-button em-dash vs comma, Set-password title, empty-state wording, GuestName body.
- swift sponsor-banner corner radius 18 → AsiCornerRadius (≈22) to match Android.
- Terms shown as two rows (Usage + Law-firm) vs our combined row; app-version line; DOB picker presentation; status-pill spacing; tile aspect/height confirm.
- Activity timeline marker: ours is outcome-based (arguably more useful) vs member-client's kind-based — likely keep.

## Open decisions

1. **B1 (money consolidation)** — do we restructure Account to member-client's single "Payment & plan" screen, or keep our panes? Big IA change.
2. **State/subdivision picker** — we ADD one on the address step; neither member-client nor CodePen has it (they infer from ZIP). Keep (data quality) or remove (parity)?
3. Whether A5 (IntroVideo) and A4 (TravelPrompt) are wanted at all.

## Recommended order

Verify-then-build A1/A3/A6 (member-facing, contained) → decide B1 → A2/A4 → B2/B3 →
batch D. Skip C. Confirm everything on device (emulator + member-client side by side).

---

## Phase 2 — execution log (batch 1, branch `mirror-member-client-ui`)

Greenlit scope: "contained gaps + polish" — A3, A6, A2, A1 + D. B1 approved but
deferred to a later batch. All landed on `mirror-member-client-ui` (not yet
merged to dev), tests green on both apps.

- **A6** — "Licensed Attorney Connected" connect banner. kotlin `80…` / swift.
- **A3** — Support pane + Account row (email row → mailto, "Phone support — coming
  soon"). New `ic_row_support` glyph both platforms. kotlin `61e93f1` / swift `6104142`.
- **D polish** — swift sponsor-banner corner radius → `AsiMetrics.cornerRadius`. swift `336a0f2`.
  (Sponsor-carousel over-stretch fix — banner aspect 3.1→4.0 to match the 4:1 art — shipped
  alongside, both apps.)
- **A2** — Appearance theme selector (System/Light/Dark) in Settings. The theme
  *system* already existed; this adds the user control + a persisted `ThemeStore`
  (mirrors the language pref), applied at the app root so the whole app re-themes.
  kotlin `75b6a4e` / swift `fdb10e0`.
- **A1** — PIN & Security row under Protection → change/set-PIN wizard. Change-only
  (no OTP recovery, per decision). Reuses the existing isPinSet / verifyMemberPin /
  setMemberPin APIs (NO new mutation): verify current PIN (skipped when none set) →
  new PIN → confirm. Reuses `AsiPinPad` + the shared 4-digit standard. New
  `ic_row_lock` glyph both platforms. +5 wizard tests each side.
  kotlin `c739ce1` / swift `f95dcd3`.

### Decisions taken during execution
- **PIN length**: kept 4 (member-client allows 4–8) — our whole PIN UX (Setup,
  call-end gate, `AsiPinPad`) is 4-digit; a 6-digit change would desync the gate.
- **Current-PIN gate**: mobile has no `changeMemberPin` mutation, but `verifyMemberPin`
  + `setMemberPin` compose to the same guarantee (backend verifies current either way),
  so no backend dependency was added.
- **PIN row placement**: under **Protection** (mirrors member-client's AccountScreen),
  not Settings where our Change-password row lives.

### Still open / next
- **B1** money consolidation — APPROVED, deferred. Biggest IA change; do as its own batch.
- Not started: A4 TravelPrompt, A5 IntroVideo (both still "wanted at all?" — open), B2/B3/B4.
- Branch not merged to dev yet — batch 1 is a reviewable unit on `mirror-member-client-ui`.

---

## Phase 2 — batch 2: B1 money consolidation (branch `mirror-member-client-ui`)

**B1 turned out much smaller than the audit feared.** The audit assumed we were
over-split (separate Plan/Payment/Family/Receipts screens). In reality both apps'
`PlanPane`/`planPane` were ALREADY member-client's hub pattern: a plan card + nav
rows to Payment method, Family, Billing history. And member-client itself does NOT
inline everything onto one scroll — PaymentAndPlanScreen is a hub that PUSHES to
`saved-cards` / `add-subaccount` / `invoices`. So the detail panes were correct to keep.

The only genuine divergence was the **entry points**: a "Plan Details" row (Account)
plus a redundant "Family members" row (Protection). Fixed to match member-client's
single row:
- "Plan Details" row → **"Payment & plan"** (opens the same hub); pane title +
  delete-account footnote renamed to match.
- Removed the duplicate "Family members" row from Protection — family is reached
  only via the hub now (member-client surfaces sub-accounts inside Payment & Plan).
  Protection is now Emergency contacts + PIN & Security.

Presentational only; no ViewModel/data change, all existing tests still green.
kotlin `abf846c` / swift `f146572`.

**Deliberately NOT added:** a separate "What's Included"/plan-detail screen
(member-client has one; our hub's plan card already carries that info — adding a
screen would be scope creep, not consolidation). Deeper inlining (card form /
roster / receipts on one scroll) was rejected — it would DIVERGE from member-client's
own hub+detail pattern.

### Batch status
- **Done on branch:** A6, A3, D, A2, A1 (batch 1) + B1 (batch 2). Not merged to dev.
- **Open:** A4 TravelPrompt, A5 IntroVideo (still "wanted at all?"), B2/B3/B4. Merge-to-dev decision pending review.

---

## Phase 2 — batch 2 REVISED: B1 exact mirror of Plan Details

Samson's follow-up: "Design it to mirror member-client exactly." My batch-2 pass
kept our labels and folded inclusions into the hub; this redoes it to match
member-client's PaymentAndPlanScreen + PlanDetailScreen precisely. kotlin `320ca7b`
/ swift `c8921c3` (both tests green).

Corrected from reading the actual source (not the scout summary):
- The screen title is **"Plan Details"** (member-client's `PAYMENT_AND_PLAN_TITLE`
  = "Plan Details"; the file is *named* PaymentAndPlanScreen but that string is not
  displayed). My "Payment & plan" rename was wrong -> reverted.
- member-client is a **hub + detail** pattern, not one inline scroll: the hub PUSHES
  to saved-cards / add-subaccount / invoices / plan-detail. We keep our sub-panes.

Exact structure now:
- Rows in order: **Payment Info** (card line + "Update") · **Sub Accounts** (only
  covered > 1; "N of M Spots Filled.") · **What's Included** · **View Invoices**.
- Plan card: **base plan price** as the heading (not the seat-inclusive total),
  "You and X members", one status+renewal line.
- New **"What's Included"** screen (member-client's PlanDetailScreen): blurb,
  primary/sub-account badge, "Subaccounts N of M used" tile, Add Subaccount /
  Manage membership CTAs.
- Empty state "No active membership" + View plans.
- Derived strings ported verbatim from `lib/paymentAndPlan` (spellNumber,
  spotsFilled, coveredSummary, subaccountsUsed, formatExpiry) with a unit test each side.

### Decision: Delete Account REMOVED (Samson confirmed)
member-client pulled the in-app "Delete account" (David 2026-08-31 §2.7) from both
Plan Details and Settings; deletions go through support. Samson chose "remove it
(mirror exactly)". Entry points gone on both apps; the capability stays (closeAccount
+ CloseAccount pane + tests) with no UI door -- support processes deletions.
**Compliance flag:** self-service right-to-delete is now support-mediated; worth a
GDPR/CCPA check with legal.

### Decision: plan card matches member-client (Samson confirmed)
Overrides the earlier CodePen "keep 'You + N members' / show total" note for THIS
card only. Now "You and X members" + base unit price. (The Home/Overview
`membershipCard` is untouched -- still "You + N".)
