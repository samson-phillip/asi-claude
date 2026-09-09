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
