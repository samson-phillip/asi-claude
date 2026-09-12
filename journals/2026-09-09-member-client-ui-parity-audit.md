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

---

## Phase 2 — batch 3: Home screen parity (branch `mirror-member-client-ui`)

Samson logged in and said Home still didn't look like member-client. Scouted
member-client's HomeScreen.tsx vs ours: member-client's Home is deliberately
minimal (a comment there: the CEO had the membership + location summary cards
removed -- "Home is for reaching an attorney"). Two divergences reversed prior
deliberate choices, so confirmed with Samson before ripping out:

- **Shield hero REMOVED** (Samson: "remove, match m-c"). member-client has no
  hero; the situation tiles are the connect surface. Biggest visual mismatch.
- **Plain tile grid** (Samson: "match m-c"). Dropped the "What's happening?"
  heading, the Change/Choose picker and the 3-slot dashed grid -- reverses the
  earlier situations-first ask, but that's the parity call.

Mirrored the rest without asking: single "Welcome back, {name}" greeting; pill
copy ("Active 24/7 Coverage." / "Grace Period -- Renew to stay covered." /
"Guest user explorer"); grace card moved UP under the pill (bordered card + gold
"Pay Now"); added the guest CTA ("Tap here to view pricing plans"); readiness card
moved BELOW the tiles. Tour's Shield step re-anchored to the tiles + reworded.
Removed the dead ShieldHero + SituationSlots + dead imports.

Nothing lost behaviourally: the situations picker sheet + the connect tray stay
wired, just unreachable from Home (like member-client). kotlin `2d2e4af` / swift `a7d4458`.

### Both PRs open into dev (no reviewers, per Samson)
- kotlin PR #1, swift PR #1 -- auto-updated with A1/A2/A3/B1 + Home.

### Still open
- A4 TravelPrompt, A5 IntroVideo -- "wanted at all?" undecided. B2/B3/B4 polish.
- On-device pass alongside member-client still needed before release.

---

## Phase 2 — batch 4: A4 TravelPrompt + A5 IntroVideo (branch `mirror-member-client-ui`)

Samson: "add them and also notify innocent." Both built on both apps.

**A4 TravelPrompt** (kotlin 88b5b3b / swift d25c912). member-client's prompt,
LIGHT version. The scout missed that member-client's TravelPrompt sets a
currentISO2 routing OVERRIDE that we don't have -- our call routing already reads
the live device timezone (TimeZoneCountry), so a travelling member is auto-connected
to attorneys where they are. So "I'm travelling" just acknowledges + suppresses the
destination 30 days; "I've moved here" -> support (billing/product change); "Not now"
suppresses. member-client's copy is kept verbatim (its promise holds via auto-routing).
Ported travelDetection (partial tz->ISO2 map, shouldPrompt, 30-day dismissal) +
its own decision tests. Home country = profile.countryId; never for guests.

**A5 IntroVideo** (kotlin c7c70a1 / swift 2b29e63). Account -> "Intro video" ->
member-client's IntroVideoScreen. Used the platform players (Android VideoView /
iOS AVKit) -- NO new media dependency. Ported getSplashVideoUrl (org media assets
then platform App Content, lenient splash_video match) + the matcher tests. Shows
the honest placeholder until a video is published.

### BACKEND DEPENDENCY -> Innocent (A5)
The Intro Video shows the placeholder until the gateway serves a splash video.
Mobile needs, from Innocent:
  1. Confirm `adminMediaAssetsByOrganization(organizationId)` and
     `appContentMediaAssets` are live on the gateway, returning
     `{ assetKey displayName filePath mimeType isActive }`.
  2. A "Splash Video" media asset actually PUBLISHED (org override or platform App
     Content) with a playable https `filePath` (not an s3:// key), matching key
     `splash_video` / `splash-video` / display name "Splash Video".
  3. Which scope on dev -- platform-wide, or per-org?
Until then both apps correctly show "Your intro video will appear here once it's published."

### Batch status -- all on branch, both PRs (#1) open into dev
Shipped: A1 PIN, A2 theme, A3 Support, A6 (verify-only), D polish, B1 Plan Details
(exact mirror; Delete Account removed -- compliance flag), Home parity, A4, A5.
Remaining audit items: B2/B3/B4 (low polish). On-device pass still needed pre-release.

---

## Phase 2 — batch 5: B2/B3/B4 layout polish (branch `mirror-member-client-ui`)

- **B2 SHIPPED** (kotlin c1b81bc / swift 4f377b3): Profile First+Last names now a
  two-column row (member-client's grid), not stacked.
- **B4 SHIPPED** (same commits): family roster entry collapsed to ONE row -- avatar
  + name + passive "Invite sent"/"Active" status + email, actions compact on the
  right. member-client's row has only remove; Resend kept as a small link (no
  capability lost). The audit's premise ("invite sent / Resend on one row") was
  slightly off -- member-client has no per-row Resend at all.
- **B3 -- NO CHANGE (decision).** kotlin ALREADY has an in-app DocumentViewer
  overlay (PdfRenderer, images) mirroring member-client's DocumentViewer, built
  because Android's ACTION_VIEW sent the member out of the app. Swift uses
  QuickLook, which is ALSO in-app (a modal) and the native iOS idiom -- same
  "stay in-app" goal met. A custom SwiftUI overlay would be maintenance for
  marginal gain, so QuickLook stays. (The scout mislooked at kotlin's text Legal pane.)

## MIRROR INITIATIVE COMPLETE
All audit items resolved: A1 PIN, A2 theme, A3 Support, A6 (verify-only), D polish,
B1 Plan Details (exact; Delete Account removed), Home parity, A4 TravelPrompt,
A5 IntroVideo (backend-dep flagged to Innocent), B2, B3 (kept native), B4.
Both PRs (#1) open into dev. Only remaining: on-device pass before release; A5
shows a placeholder until Innocent publishes a splash video.

---

## Phase 2 — batch 6: bottom tab bar (branch `mirror-member-client-ui`)

member-client's tabs are **Home · Docs · History · Account** -- the SAME
destinations we already had, just member-client's names: Docs = our Glovebox,
History = our Activity, Account = our "Profile" tab. So this was labels + one icon,
not a re-order (the scout initially mis-read it as swapped destinations).

kotlin c75fe19 / swift 0298e6c:
- Tab labels -> Docs / History / Account (from Glovebox / Activity / Profile).
- New **ic_tab_docs** document glyph (member-client's `docs`). The History clock
  (`ic_tab_activity`) and Account user (`ic_tab_profile`) glyphs were ALREADY
  member-client's, so only the Docs icon changed.
- Activity screen title + the tour's Activity step reworded to "History" so the
  tab and its screen agree.

### Residual "Glovebox" naming (FLAG, not done)
The tab now says "Docs" but "Glovebox" still appears in: the tour Glovebox step
("Your Glovebox, always ready"), the Account "My documents -> Your Glovebox" row,
and the feature/screen internals. member-client uses Documents/Docs throughout.
A full Glovebox->Docs rename is broader than "the tabs" -- left for Samson to call.

### Build note
Disk hit 99% mid-work; cleared Xcode DerivedData + old simulators + device support
(freed ~20Gi). That forced a fresh clone of the 2.4M-object Stripe SPM package,
which flaked on the network twice before succeeding. Built with
COMPILER_INDEX_STORE_ENABLE=NO to avoid the index datastore that filled the disk.

---

## Phase 2 — batch 7: Account hub row inventory (branch `mirror-member-client-ui`)

Samson-approved via the divergence review: add the 3 missing rows, strip
sub-labels to member-client's bare style, + polish (More order, Personal Info
icon, PIN wording).

kotlin d1a0e59 (VERIFIED: compileDebugKotlin + processDebugResources green):
- Added rows: **Finish Your Profile** (top of Account -> Destination.Completion,
  the setup checklist), **History** (Account -> Destination.Activity), **Share**
  (bottom of More -> OS share sheet, no chevron).
- Stripped descriptive sub-labels -> bare rows; kept only Plan (live rate), PIN
  (unset warning), Finish-Your-Profile (fixed prompt).
- More reordered to Intro Video -> Support -> Settings -> Share.
- Personal Info icon -> new ic_id_card (kotlin+swift previously disagreed; neither
  was web's id-card).
- PIN sub-label: "...during a consultation", em-dash, only when unset.
- New glyphs ic_check_circle / ic_id_card / ic_row_share (History reuses the
  history clock). AsiNavRow gained an optional `chevron` flag (Share = false).

swift b0bb296 (NOT build-verified -- see below): full mirror. Share uses SwiftUI
`ShareLink` (cleaner than an app closure). Three imagesets added.

### Scout correction
The scout claimed the avatar had "no camera badge / nothing uploads an avatar" --
STALE. Verified the EditableAvatar + camera badge + presigned upload are live
(profile photo shipped). Not a divergence; left alone.

### Decision flagged for Samson
"Finish Your Profile" shows UNCONDITIONALLY (mirrors member-client, which doesn't
hide it once complete). May want gating on profile-completion later.

### BLOCKER: disk + Stripe SPM clone
Machine hit 100% disk repeatedly (down to ~2Gi; even Bash output-capture ENOSPC'd).
Cleared DerivedData/simulators/device-support/gradle caches/TM snapshots, and
(Samson-approved) ~/Library/Caches (~8.7G). Each DerivedData wipe forced a fresh
clone of the 2.4M-object Stripe SPM repo, which flaked on the network
("fetch-pack: invalid index-pack output") on EVERY swift-Account attempt. So the
swift Account commit is UNBUILT. kotlin is verified. Needs a local `xcodebuild`
on swift before merge; watch ShareLink + the two new AccountScreen params.

### Resolved: swift build verified
Samson freed disk (68Gi). swift b0bb296 rebuilt from scratch (fresh Stripe SPM
clone) -> **BUILD SUCCEEDED**, no errors. ShareLink, the two new AccountScreen
params + wiring, the AsiNavRow `chevron` flag, and all three imagesets compile.
No code fixes were needed -- the unbuilt commit was correct. Batch 7 is now
green on BOTH apps; no pre-merge build caveat remains.

### Follow-up: gate "Finish Your Profile" on completion (Samson's call)
Diverge from member-client (shows the row always) -> hide it once setup is done.
kotlin 4575dcb (compileDebugKotlin green) / swift 0e43004 (BUILD SUCCEEDED).
Gate = `ProfileReadiness.isOnboarded` (the DURABLE signal, already used for
routing; NOT allDone, so a later-added checklist row won't resurface the menu
entry). Row hidden until readiness loads -> no flash for a finished member.
Readiness was only loaded on the checklist screen, so both apps now load it on
Account entry too (swift: `.task { completion.load() }`; kotlin: Account branch
spins up the Activity-scoped, shared completion VM + LaunchedEffect load).
The earlier "shows unconditionally" FLAG is now resolved.

---

## Phase 2 — batch 8: Docs/Glovebox field-type parity (branch `mirror-member-client-ui`)

Samson flagged the Docs screen didn't match member-client. Mapped all three
(reference DocumentsScreen.tsx vs kotlin/swift GloveboxScreen) via two Explore
agents. Finding: the apps are near-identical mirrors of each other and diverge
from the reference the same way. **Root gap: field-type coverage.** Both apps'
`DocumentFieldKind.fromWire` only mapped text/dropdown/file/image; the reference
renders eight types, so number/date/textarea/radio/select/yes-no all collapsed to
`Unsupported` ("not supported in the app yet").

Samson chose: **typed fields + quick wins**, and **keep the system picker** (don't
build the MOBILE #143 Camera/Gallery/Documents sheet -- documented CodePen-rule
decision, re-confirmed).

Shipped (kotlin 8ab45d5 VERIFIED / swift 791c4b3 VERIFIED):
- DocumentFieldKind += Textarea/Number/Date/Radio/YesNo; fromWire maps the
  yes-no family (checkbox/boolean/toggle/…) and select/choice -> Dropdown.
- FieldRow renders each: number (numeric keyboard), **date = validated
  YYYY-MM-DD typed field** (kept typed, NOT a native picker, so both platforms
  match -- a follow-up could make it a real picker), textarea (multi-line),
  radio (selectable group), yes-no (switch, stored "yes"/"no").
- Validation mirrors member-client: required can't save empty + number must be
  numeric; per-field messages block the save. Cleared on edit / cancel / back.
- Required "*" shown (red on explicit labels; appended to floating labels).
- Footer security line (#139) at the foot of the Glovebox (our "Law Firm
  Representative" wording, not the reference's "legal first responder").
- kotlin only: remote (URL) section icons now load via Coil (already a dep),
  tinted code glyph beneath as fallback. Swift already loaded them.
- Shared components gained: kotlin AsiTextField `minLines`; swift AsiTextField
  `keyboardType` + `axis`. All defaulted; existing call sites unaffected.

Verified: kotlin compileDebugKotlin + GloveboxViewModelTest 30/30 + DocumentKindTest 7/7;
swift BUILD SUCCEEDED + GloveboxViewModelTests TEST SUCCEEDED. member-client pulled
to dev @ 22565a2 first.

### Deliberately NOT changed (documented divergences, left per Samson / CodePen rule)
- Camera/Gallery/Documents upload sheet (#143) -> single system picker.
- Summary card counts SECTIONS not documents (a section holds many fields).
- Nav model: our section-list -> section-detail drill-down vs the reference's
  one-screen-with-group-titles.
- Upload tile uses a gold glyph, not the reference's crimson/check tile.

### Follow-up: Account hub — PIN row style + Finish-Profile visibility (from a screenshot)
Samson shared an Android Account screenshot (John Doex, onboarded). Two fixes,
kotlin 9410bd4 / swift 1b94e84 (both build-green):
- **PIN & Security** rendered as a bordered card with no icon/chevron — the only
  `divided=false` row in a flat hairline list. Flipped to `divided=true`; now draws
  the lock glyph + label + chevron like every other row.
- **Finish Your Profile** shown UNCONDITIONALLY again. member-client AccountScreen.tsx:147
  renders it with no completion condition, and Samson asked for it "like the member
  client" — so this REVERSES the completion-gating from 4575dcb/0e43004 (which had
  hidden it once onboarded, i.e. why it was absent for John Doex). Removed the
  showFinishProfile param + the readiness load from the Account branch on both apps.
  (Net: back to the original mirror behaviour. The gate was a round-trip.)

### Bugfix: checklist auto-closed on explicit entry (fallout from ungating Finish-Profile)
Samson: "the finish your profile screen auto closes; likewise tapping the protection
readiness button auto closes that screen." Root cause: the Completion/checklist
screen auto-skips onboarded members to Home ("don't strand them there"). That skip
fired on ANY first entry (swift `completionChecked` @State; kotlin `autoSkipChecked`
remember). Once Finish Your Profile became unconditional (9410bd4/1b94e84), an
onboarded member could tap into the checklist -- from Account's Finish Your Profile
OR Home's readiness/finish-profile button (both -> Destination.Completion) -- and
got bounced straight back out.
Fix (kotlin fd49476 / swift dc7c5b1, both build-green): scope the auto-skip to the
POST-LOGIN LANDING only, via a `checklistFromLogin` flag armed at the two login
landings (login success + guest-name save) and consumed on the checklist's first
load. Explicit taps leave it false -> checklist stays open. Returning onboarded
members still skip it at login (unchanged).

### Docs screen: Glovebox -> Documents verbiage (screen only)
Samson: "the app still has glovebox verbiage" on the Docs screen. Fixed the
Docs-screen copy on both apps (kotlin 2b3edb3 / swift 41d5301, build-green):
heading "Digital Glovebox" -> "My Documents"; card eyebrow "ENCRYPTED GLOVEBOX" ->
"ENCRYPTED DOCUMENTS"; checklist subheading "Stored in your Glovebox ..." ->
"Stored securely ..."; "Loading your Glovebox" -> "Loading your documents"; the
load + upload error strings -> "... your documents."
SCOPED to the Docs screen (Samson chose "Docs screen only"). "Glovebox" is KEPT as
a brand term in the guided tour ("Your Glovebox, always ready."), the Welcome
carousel ("Digital glovebox") and the Home nudge -- member-client keeps "Glove Box"
in exactly those spots (its own summary card still reads "Digital Glove Box.").
Don't strip those without a new decision.

### Docs screen — two more rounds from Samson's screenshots

**Title block (kotlin cdf4167 / swift 6fcd006):** matched member-client's
DocumentsScreen header on the Docs tab — a small centred "My Documents" over the
big "Upload Your Documents." + the exact subheading "Stored securely and accessible
to your legal first responder only during calls." Footer line adopts member-client's
"legal first responder" wording too. Samson scoped this to the title block + copy
(not the card / field list), and chose "match member-client" on the
first-responder-vs-Law-Firm-Representative terminology (Docs screen only).

**Empty-docs bug (kotlin d3dc459 / swift c29a951) — the important one.** Account
salmson93@gmail.com: member-client lists 7 fields (CONTRACT/FORM groups: Service
Agreement, example 5, Incident Initial Report Form…), our app showed "No document
sections are configured yet." Root cause: `DocumentFieldKind.fromWire` mapped any
unmapped wire type (agreement/form/example/policy/…) to `Unsupported`, and `load()`
drops a section whose fields are all non-member-input → every section vanished for
this account. member-client has NO such filter — its renderTypedField defaults an
unknown type to a plain text input. FIX: fromWire default `Unsupported` -> `Text`,
so unknown types render as text and their sections show. file/image stay uploads;
Unsupported kept as a defensive sentinel, no longer produced. This REVERSES the old
deliberate "keep org templates out" exclusion (it diverged from member-client).
Tests updated on both apps (unknown->text/member-input; "Policy" section now appears;
usable-glovebox count 3->4). Verified: kotlin 30/30, swift TEST SUCCEEDED.

REMAINING HYPOTHESIS if still empty for some account: the field query country param
— member-client sends the member's `location.effectiveISO2`; we send device
`TimeZoneCountry.current()`. Org-template fields aren't country-gated, so it wasn't
the cause here, but a country mismatch could still starve country-specific fields.

### Docs country param — checked, and a second cause of the empty screen
Samson asked to check the field-query country param (my flagged fallback hypothesis).
Confirmed a real, systemic divergence:
- Our app tailors the doc-field query by the DEVICE TIMEZONE (`TimeZoneCountry.current()`).
  member-client tailors by the member's HOME country resolved from their profile, and
  sends `null` = "no filter, show everything" when the profile has no country
  (memberCountry.ts getHomeCountryISO2: "Callers must treat null as no filter... a
  member who can't see any [fields] would think the app was broken"). A country value
  NARROWS the set, so a device tz that isn't the member's country narrowed it wrongly
  → a second cause of salmson93's empty screen, on top of the field-kind drop.
FIX (Samson chose "send null now"): kotlin 40a1388 / swift 521d778 — the doc query
sends `countryISO2 = null` (member-client's no-country fallback), so the member always
sees their own docs. Verified kotlin 30/30, swift TEST SUCCEEDED.

TWO LATENT BUGS found along the way (NOT fixed — flagged for a follow-up):
1. **`profile.countryId` is the opaque country RECORD ID, not an ISO2** (address form
   sets `countryId = country.id`; `Country` has both `id` and `iso2`). Yet
   `HomeViewModel.maybePromptTravel` compares `profile.countryId` to a detected ISO2 —
   so the "I'm travelling" prompt almost certainly NEVER fires. Resolving home→ISO2
   needs `listCountries()` (id→iso2).
2. **Call routing (`CallViewModel.currentCountry`) also uses device tz** by a deliberate
   in-code note — diverges from member-client's home-country routing.
PROPER FOLLOW-UP: a shared "member home country ISO2" resolver (profile country → ISO2
via listCountries, current ?? home ?? null, cached) used by Docs + Home incident types
+ call routing — mirroring member-client's memberCountry.ts / location.tsx. Bigger,
product-level; not done.

### Shared home-country resolver + Android Back button (Samson)

**MemberCountry resolver** (kotlin 43eb196 / swift ce6e8fc, both build+test green).
Built the shared "member home country" resolver member-client has (memberCountry.ts):
resolves the profile's country to an ISO-2, cached per member, cleared on sign-out.
The profile's `countryId` is an opaque RECORD id (not ISO-2), so it matches the
countries list by id OR iso2, with a 2-letter-code fallback (the gateway's field
naming is inconsistent, and the tests use ISO-2-as-countryId). Wired into:
- Docs field query -> home ?? null (supersedes the interim null; real tailoring).
- Travel detection -> resolved home ISO-2 (fixes the compare-opaque-id-to-ISO-2 bug,
  so "I'm travelling" can actually fire; also warms the cache).
- Call routing (currentCountry) -> the warm home ISO-2, not the device timezone
  (the Kenyan-member-to-California bug). swift default is nil; the app root passes the
  resolver closure (default args can't see `session`). kotlin default reads it directly.
Cache is process-global, so tests reset it between suites (a glovebox resolution was
leaking into the home travel-detection tests). Robust-resolver note: matching id OR
iso2 + 2-letter fallback means it works whether `countryID` is opaque or already ISO-2.

**Android Back button** (kotlin 6cd0b86). The nav is a when(destination) with no back
stack and no BackHandler -> hardware/gesture Back closed the app from every screen.
Added a fixed screen-hierarchy Back (NOT a history stack, which would land Back on a
programmatic redirect like the checklist auto-skip / post-login landing): a root
BackHandler maps each screen to its parent; Account + Glovebox add their own to pop an
open sub-pane first; a live call swallows Back (never exit the app or drop the call).
iOS unaffected (no hardware Back; on-screen chevrons already do this). Verified by
compile + a scenario trace over all 14 destinations, NOT a live emulator run.

### Login screen verbiage aligned to member-client (Samson)
kotlin 775a884 / swift 3d76fb0, both build-green; iOS login verified live on the
simulator (demo route, reverted after). Mapped our LoginScreen against member-client's
and aligned:
- **No eyebrows** anywhere (removed SIGN IN OR SIGN UP / VERIFY / EXPLORE AS A GUEST /
  SIGN IN; Heading's eyebrow is now optional). Samson chose to drop them.
- **Email step = member-client's hero**: "Take control of your freedom" + "Enter your
  email and we'll send you a secure sign-in code." + button "Next". Samson chose this
  over keeping our honest "the code creates your account" warning (documented tradeoff:
  a mistyped email still provisions an account, but the reference doesn't surface it).
- Guest: "Explore as a guest" (no period), "We will email you…" (was "We'll"),
  placeholders "First name"/"Last name" (were "Jordan"/"Avery"), "Already Registered? Login".
- Dropped trailing periods ("Verify it's you", "Welcome back"); busy labels
  "Sending…"/"Signing in…"/"Verifying…".
- LEFT the login ERROR strings as-is: member-client's "…Try password sign-in" is wrong
  for the guest send path (shared message). Flag if full error parity is wanted.
kotlin DynamicTypeTest updated to the new copy. One visual nit vs member-client: "freedom"
is plain white here, gold-gradient there — verbiage matches; the gradient is an optional
follow-up.

### Login: added the missing shield logo to the hero (Samson)
Samson: the login hero was missing the shield logo member-client shows above the
heading, and pointed me at member-client for the asset. Our own brand_shield.png is
malformed (clipped/streaked -- ShieldLockup already dodges it by using the SVG), so
I imported the reference's asset verbatim: member-client/public/asi-gold-logo.png ->
swift asi_gold_logo.imageset (3x) + kotlin drawable-nodpi/asi_gold_logo.png. Wired it
into the shared login Heading: centred gold shield (72pt) with a soft gold glow over a
now-CENTRED heading + subtext, on every auth pane (matches member-client). kotlin 480f6f5
/ swift 88dd47e, both build-green; iOS login hero verified live on the simulator (demo
route, reverted). Remaining nits vs the reference (optional): "freedom" gold-gradient;
the password button reads "Login with account password" there vs our "Use your password
instead" (+ leading lock/user icons on those buttons).

### Login polish + intro-once flow (Samson)
kotlin 73aa547 / swift d4af90d, both build-green; iOS verified live. Four items:
1. "freedom" in the email hero tinted gold (member-client gradient) -- Heading gained
   a `highlight` param (AnnotatedString kotlin / concatenated Text swift).
2. Shield logo faint gold glow (kotlin: radialGradient behind; swift: shadow 0.35/30).
3. Disabled PrimaryButton -> FAINT active gold (ctaBg @ ~0.3) instead of navy border,
   with faded ctaFg text. App-wide (member-client's disabled style).
4. **Intro-once**: Welcome shown only on first launch; a returning member or a signed-out
   user goes straight to Login. Persisted flag (kotlin SharedPrefs `intro_seen` via a new
   `markIntroSeen` AppRoot param; swift UserDefaults `asi.introSeen`). All sign-out routes
   Welcome->Login. Login LOST its Back button (member-client's email step has none); the
   Android system-Back backTarget makes Login a root (GuestName->Login). Register stays
   reachable (Welcome Register = web checkout; login keeps guest + email-code account creation).
My opinion given + Samson agreed. Optional nit remaining: disabled-gold reads slightly
olive at 0.3 over navy -- can bump opacity if wanted. Also still open: password button
"Login with account password" + button lead icons (member-client) vs ours.

### Intro-once REVERTED (Samson's re-decision)
Samson reconsidered the intro-once flow: on a SHARED DEVICE, hiding Welcome after the
first launch made the "Register" (web checkout) unreachable for a second person. I
advised the gap was narrow (login's guest + email-code flow still create accounts; only
the paid web Register on Welcome was blocked) and offered: keep-intro-once + add a
Register link, revert, or leave as-is. Samson chose REVERT. Cleanly reverted just the
flow files (kotlin 8295eb5 MainActivity / swift df293e4 AttorneyShieldApp) back to their
pre-intro-once state via `git checkout <login-logo-commit> -- <file>` -- always show
Welcome, login Back button restored, sign-out -> Welcome. The three login visual polish
items (gold "freedom", faint logo glow, faded-gold disabled button) are in LoginScreen +
AsiComponents and STAY. So: no intro-once, don't re-add it.

### Intro-once RE-APPLIED (final, confirmed vs member-client)
Samson: "show it once, like the member client." Checked member-client: it DOES gate its
onboarding carousel on `hasSeenOnboarding()` (App.tsx: showIntro = !hasSeenOnboarding();
"a returning member who signed out goes straight to Login"; OnboardingScreen has
Register + Log in on every slide, marks seen on leave). So intro-once IS member-client
parity, and member-client handles the shared-device Register the same way we do (Register
on the first-run Welcome + login's guest/email account creation). Re-applied by restoring
the two flow files to the intro-once commit (kotlin 5e58e01 / swift 83637a7). NET after
the flip-flop: intro-once is ON (final). Visual polish (gold freedom / glow / faded button)
was never touched by the flip-flop.

### Login OTP verify: channel chooser (email / phone)
Samson: "checkout the login otp verification screen to match the member client …
add the email or phone number verification options." member-client's OtpStep
(LoginScreen.tsx 373-387) renders a "Channel choices" list ABOVE the code boxes:
an EMAIL row always (masked email), an SMS row only when `otp.maskedPhone` exists,
each an .lr-icon medallion + masked destination + a check-circle on the active
channel; tapping the inactive row = `onResend(channel)` (re-send + switch). No
`.list-row.on` CSS exists — the check is the only selected-state cue.

Mirrored on both apps:
- kotlin: new ChannelChooser/ChannelRow in CodePane; ic_mail + ic_phone drawables
  ported from icons.tsx (stroke-only, tinted at use). onResend became
  (OtpChannel)->Unit; dropped the standalone "Send by text" link + onSendByText.
  Copy: body loses "…to <dest>" (rows show it); footer "Didn't get a code?" →
  "Didn't receive a code?" (member-client wording). Fixed AccessibilityTest +
  DynamicTypeTest call sites/copy.
- swift: channelChooser/channelRow in codePane; SF Symbols envelope/phone +
  checkmark.circle.fill; same copy + drop of the send-by-text button.
- Verified render on iPhone 16 Pro sim via a temp env-gated LOGIN_CODE_DEMO route
  (seeded masked email+phone), screenshotted, then reverted the scaffolding clean.
  Screenshot confirmed: mail row (gold check) over phone row, correct copy.
Builds green both sides; login JVM unit tests pass. Pre-existing unrelated break:
ScreenRenderTest.kt (CallScreen signature drift) blocks the androidTest set — not
mine, HEAD 204ecfe, left as-is. Commits kotlin af19399 / swift 9a53839.

### Bug: sign-out after OTP lands on the code pane, not the email pane
Samson: "when you logout after using otp verification to logout, the user is
landed to the otp verification screen instead of the login screen." Root cause:
the LoginViewModel is long-lived (kotlin: Activity-scoped `viewModel()`; swift:
`@State` in RootView, whole app session), so a code sign-in leaves it parked on
`step = code` with a stale masked destination. Routing back to sign-in re-shows
that pane.

Fix: added `LoginViewModel.reset()` (→ pristine email pane, countdown cancelled)
and call it on every entry into sign-in.
- kotlin: one guarded reset in the Destination.Login branch —
  `var didResetLogin by rememberSaveable{false}; if(!didResetLogin){reset();…}` —
  fires once per real entry but survives a config change (composition recreate)
  so rotating on the code pane doesn't bounce you off mid-verify. Runs before the
  prefillEmail LaunchedEffect, which re-fills after.
- swift: `.onAppear` would clobber the deep-link prefill (set at the transition,
  before the view appears), so instead reset at each route to `.login` — the S3
  session-ended, the checkout-return prefill (reset THEN set email), Welcome→login,
  and all three signOut sites.
Unit-tested both (LoginViewModelTest/Tests: reset from code pane → email pane,
fields cleared). Builds + login suites green. Commits kotlin d87d461 / swift c9f1709.

### Payment Methods: single-card → multi-card list (member-client Saved Cards)
Samson: member-client accepts multiple cards, lists them, one can be made default —
update the app. Explored all three (3 parallel agents): member-client SavedCardsScreen
= carousel + list, per-card Make default / Remove / Add, default badge; and CRUCIALLY
BOTH apps already had the full plumbing — PaymentCard.isDefault, api list/attach/
setDefault/detach, and VM makeDefaultCard/removeCard — but the UI deliberately showed
ONE card (explicit comment: "make-default/remove wiring stays in API/VM for a future
multi-card view"). So this was a UI-only surfacing job.

Asked Samson: drop the app's edit-expiry/ZIP (member-client has none) or keep it? He
chose KEEP (superset). Result on both apps: Payment Methods lists every card (reusing
the mailing-address list pattern — gold Default pill + text actions), non-default cards
get "Make default", every card gets Edit + Remove, plus "Add payment method". Remove
asks first (kotlin AlertDialog / swift .alert: "Remove {brand} ending {last4}?"). Edit
opens a per-card sub-view (expiry/ZIP + Save) gated by a new editingCardId; a new
paneBack() pops the edit before leaving the pane (wired to the title-bar back + Android
hardware back). Title "Payment method" → "Payment Methods".

Verified the iOS list AND edit sub-view on the sim via a temp CARDS_DEMO route (two
seeded cards), screenshotted both, reverted the scaffolding clean. New unit tests both
apps (open→list, edit seeds form, paneBack pops edit, remove asks-then-detaches, cancel
keeps). Builds + full account suites green. Commits kotlin dd7e37c / swift 8e1ee40.

### Payment Methods v2: match the actual member-client screenshot (carousel + Your cards)
Samson shared the real member-client Payment Methods screenshot. My first pass (stacked
plain cards + text actions + info chip) diverged. Read the source (SavedCardsScreen.tsx +
screens.css) for exact fidelity and reworked both apps to match:
- **Carousel** (`.card-carousel`): horizontally-scrolling gradient card graphics, each
  ~86% width so the next peeks; the reference's 4 gradients (cc-grad-0..3, hardcoded hex),
  gold "chip", uppercase brand, masked number, cardholder + MM/YY; the DEFAULT card ringed
  in a 2px gold border (`.credit-card.default`).
- **"Your cards" list**: compact rows — a card medallion (kotlin ic_row_card / swift SF
  creditcard), "{brand} •••• {last4}" + "Exp. Date MM / YY" (formatExpiry = "MM / YY"),
  a GREEN Default badge (`.badge.ok`) or a gold "Make default" link, and a circular TRASH
  button (new ic_trash on kotlin / SF trash on swift).
- Footer: "+ Replace Card" (SecondaryButton ghost) with a card on file, "Add payment
  method" when empty. Dropped the info chip.
- Edit (our extra) kept: tapping a row's card body → the expiry/ZIP editor.
kotlin: BoxWithConstraints+horizontalScroll for the carousel. swift: GeometryReader +
ScrollView(.horizontal); shrank "Make default" to 15pt so the row doesn't truncate the
last4. Verified on the sim against the screenshot (near-exact). Account suites green.
Commits kotlin 2b59058 / swift a1c8e4a.

### Home: pin the sponsor carousel to the foot (member-client parity)
Samson: move the auto slider to the bottom of the screen always, like member-client.
Checked the reference: `.sponsor-carousel` is `position: fixed; bottom: safe-bottom +
tabbar-h + 24px; z-index: 35` — pinned above the tab bar, and `.screen.home-has-banner`
reserves ~150px bottom padding so content scrolls clear. Ours had the carousel as the
LAST item in the scroll (scrolled away). Fixed both:
- kotlin: wrapped Home in a Box; carousel is a BottomCenter-aligned overlay (horizontal
  window insets), and the scroll Column reserves a 150dp bottom spacer when the banner
  shows. TabScaffold already puts Home content in a Box above the tab bar, so BottomCenter
  = just above the bar.
- swift: `.overlay(alignment: .bottom)` on the Home ScrollView; content `.padding(.bottom,
  150)` when banner shows. RootView's VStack{content; AsiTabBar} puts Home above the bar.
Gating unchanged (canCall && banners non-empty). Verified on the sim via a temp HOME_DEMO
route (seeded entitled + 2 banners, fake tab bar below): the "Sponsored" slider + dots sit
pinned above the bar while tiles scroll above it; reverted the scaffolding clean. Both build.
Commits kotlin 6f40fbf / swift c2f4833.

### Account: hide the membership/plan card below the avatar
Samson: hide the plan card below the profile picture to match member-client. Confirmed
member-client's AccountScreen.tsx goes avatar → `<div className="section-title">Account`
directly — no membership/plan card between the photo and the Account list. Ours rendered
a MembershipCard there. Removed the call from the overview on both apps (kotlin OverviewPane
line 446 / swift overviewPane). Plan stays reachable via the "Plan Details" row → Plan pane,
so nothing is lost; the card component is left defined-but-unused (harmless). Verified the
iOS overview on the sim (avatar → ACCOUNT heading, no card), reverted the temp demo clean.
Both build. Commits kotlin edf1aff / swift 57572a3.
NOTE: kotlin app/build.gradle.kts had an unrelated versionName 7.6→7.7 bump (not mine) —
left uncommitted for Samson to handle.

### Innocent work-order — CRITICAL fixes 01-05 SHIPPED (both apps, 12 Sep)
Samson: work the items in the best sequence, he'll test. Did the "fix first" batch:
- 01 History hang: dropped attorneyDisplayName from commsCallsByMember.attorneyAssignments
  (kept {id status}); listCallHistory throws → "Try again" retry. kotlin e976d55 / swift f087c73.
- 05 Storefront ?from=app in AsiConfig.planUrl. kotlin c234c6e / swift 05f23b1.
- 04 Report member-ended calls: commsUpdateCallState(completed, endedAt, member_pin|member_cancelled)
  in end(), best-effort NonCancellable/detached Task; backend outcomes stay comms'. kotlin c449625 / swift 76b1df6.
- 02 Keep screen awake in calls: kotlin View.keepScreenOn / swift isIdleTimerDisabled for the
  CallScreen lifetime. kotlin 0a4c4d4 / swift 71fae07. (Android FG-service = separate follow-up.)
- 03 PIN 4→4-8, no auto-submit, Confirm button. All surfaces on AsiPinPad (dots grow 4→8);
  Setup keeps its Continue button; Account-change + call-end got Confirm buttons; tests updated.
  kotlin 13ac2e2 / swift b4c0e7b.
All build; PIN + activity + account unit suites green. Disk hit 0 mid-item-03 (recurring) —
cleared DerivedData/*/Build + gradle transforms (kept Stripe SourcePackages), recovered.
Version bumps (kotlin versionName 7.7 / swift MARKETING_VERSION 8.01 + kotlin app/release/*)
were pre-existing worktree changes; kept OUT of the work-order commits for Samson to handle.
Next: behavioral 06-11.

### Innocent work-order — behavioral 06/07/10 SHIPPED (both apps, 12 Sep)
- 06 travel-prompt copy no longer claims cross-border routing ("We'll note that you're
  travelling") — interim until 08. kotlin 1fd771e / swift 9214f1e.
- 07 incident tiles country-scoped: listIncidentTypes(countryISO2) → adminIncidentTypeList
  (countryISO2:), passed the member's resolved home ISO2 (MemberCountry). Legal separation.
  kotlin c5a333a / swift 36fe6c0.
- 10 sign-out revokes the session: AsiApi.logout() fires `mutation{logout}` best-effort with
  the token still attached, then clears (kotlin scope.launch / swift Task). kotlin b2b2aa1 / swift e476921.
All build. Remaining behavioral: 08 (location-override persistence + currentSubdivision — a
real feature; currentCountry already sends home), 09 (Emergency Contacts CRUD — new screen),
11 (push — needs a product decision: build APNs/FCM infra vs hide the preferences screen).

### Work-order 11 — push preferences hidden (Paul's call)
Paul chose "hide" over building APNs/FCM infra. Removed the "Push notifications" row from
Account→Settings on both apps; the NotificationSettings screen stays in code, unreachable,
to restore when token registration lands. kotlin be95fdb / swift 4efcdce.
Behavioral batch now: 06/07/10/11 SHIPPED. Remaining are the two substantial FEATURES:
08 (location-override persistence — needs a per-member override store + a Current Location
picker + call currentCountry=current??home + currentSubdivision) and 09 (Emergency Contacts
CRUD — a new list screen). Each warrants its own focused pass.
