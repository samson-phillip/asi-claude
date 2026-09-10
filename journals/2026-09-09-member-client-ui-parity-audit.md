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
