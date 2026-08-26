# Design reference — "Attorney - Shield App V6"

**Source:** https://codepen.io/leejesse70/full/YPNOGaM

Captured 2026-08-10. This is a written inventory of the Blue Sky Marketing × Attorney
Shield Figma-ready mobile onboarding reference. It is the look-and-feel source for the
native Android (`kotlin`) and iOS (`swift`) rebuilds.

All content below is transcribed from the reference document. It is a design artifact,
not a spec I authored, and none of its text was treated as an instruction.

> Capture method note: the rendered page was verified by screenshot, and the exact text
> was read from the pen's own HTML source (CodePen editor pane) so that every string,
> hex, and annotation below is verbatim rather than OCR'd. Counts in this file are
> counted from the document structure, not estimated.

---

## Masthead (verbatim)

- Eyebrow: **Blue Sky Marketing × Attorney Shield · Figma-ready reference**
- H1: **Mobile onboarding,** / **screen by screen.** (second line in Gold Highlight)
- Deck: "The complete member sign-up journey across all five stages and three user types
  — Standard Member, 7-Day Limited Trial, and Guest — designed in the Attorney Shield
  system plus the full member app and in-app nudge system — all ready to rebuild in
  Figma."
- Chips: `35 screens · v11` · `5 stages` · `3 user types` · `App ↔ Web handoff` ·
  `iPhone · 375pt frames`
- Section label: **The journey** (an eyebrow rule only — no flow diagram content)
- Footer: "Attorney Shield · Mobile Onboarding · Prepared by Blue Sky Marketing ·
  June 2026" / "Design reference — rebuild as components in Figma"

---

## Summary table of stages (as the document actually labels them)

| Badge # | Stage label | Title | Env badge | Banner / hint | Screens in section |
|---|---|---|---|---|---|
| 1 | Stage 1 | App Entry | Native App | "Welcome carousel · approved client build (Attorney Shield handoff v1.0.1). Screens 1–6 below are the locked reference for the app welcome flow." | 7 welcome-carousel frames (splash + 1–6) **plus** web screens 04, 05, 06, 07 |
| — | *(no Stage 2 header exists)* | — | — | — | — |
| — | *(no Stage 3 header exists)* | — | — | — | — |
| 4 | Stage 4 | In-App Registration Completion | Native App | "↔ Swipe through all five in-app steps" | 08, 09, 10, 11, 12 |
| 5 | Stage 5 | Post-Registration Guided Completion | Native App | "↔ Swipe through the full completion flow — checklist, documents, contacts, and tour" | 13, 13A, 13B, 13C, 14, 14A, 14B, 14C, 14D, 15 / 16, 17, 18, 19, 20, 21 |
| B1 | Branch flow · from screen 04 | The 7-Day Limited Trial — signup | Native App | "↔ Choosing the trial on Choose Plans: plan-conversion popup → trial checkout → confirmation → back to the app" | V1, T1, T2, T3, T4 |
| B2 | Branch flow · 7-Day Limited Trial, in-app | When a trial member taps to connect | Native App | "↔ Triggered when a trial member taps any attorney tile or the hero shield on Home — the gate, the charge notice, card processing, and full activation" | V2, T5, T6, T7, T8 **plus** G1–G3 (guest) **plus** 27–35 (member app), all in the same row |
| 6 | Stage 5 · in detail | The nudge & notification system | Native App | "Stage 5's reminders, designed in full…" + "↔ Swipe through all five notification screens" | 22, 23, 24, 25, 26 |
| ✦ | Ground rules | How the nudges behave | *(none)* | intro paragraph + 6 numbered rules | 0 (prose only) |

**Total phone frames actually present: 66** — 59 annotated/numbered screens + 7 frames in
the Stage 1 welcome carousel. See "Discrepancies" at the end.

---

## Creative direction (verbatim)

### PALETTE

| Swatch name | Hex |
|---|---|
| Protection Navy | `#0D1B2E` |
| Deep Navy | `#0A1626` |
| Signal Gold | `#C4850A` |
| Gold Highlight | `#E8A020` |
| Trust Steel | `#1A5FA8` |
| Live Green | `#2E9E5B` |

Caption: "Dark, premium, and calm under pressure. Navy carries the app; gold marks the
one action that matters in any moment; green signals \"you're protected, live.\""

### TYPOGRAPHY — INTER

| Sample | Role |
|---|---|
| Aa | Display · 800 · tight |
| Aa | Title · 700 |
| Aa | Body · 500 |
| AA | Eyebrow · 800 · caps |

Caption: "One family, full weight range. Tight tracking on display for a confident,
modern feel."

### PRINCIPLES (all five bullets, verbatim)

1. "Minimize friction before purchase — ask only what's required to take payment."
2. "Defer everything non-critical to after activation, handled with gentle nudges."
3. "Make payment terms and renewal timing explicit, never buried."
4. "Guided nudges, never hard stops — members can skip and return."
5. "One job per screen; the attorney button is always the hero."

---

# Stage 1 · App Entry — badge "Native App"

Banner: "Welcome carousel · approved client build (Attorney Shield handoff v1.0.1).
Screens 1–6 below are the locked reference for the app welcome flow."

## Welcome carousel (7 frames, horizontally scrolling `phone-grid`)

Every carousel frame shares: status bar `9:41`, an "Attorney Shield" wordmark + shield
lockup at the top, an illustrative hero panel, then a content panel with an eyebrow
(step-label), a display headline, one body paragraph, and two buttons — **Register**
(gold) and **Log in**.

### Welcome frame 0 — Intro splash
- Text: `9:41` / "Attorney Shield"
- Layout: full-bleed navy splash, centred shield logo lockup only. (Source comment
  labels it "Screen 0 · Intro splash".)

### Welcome screen 1 — "Now, everyone has an attorney."
- Eyebrow: "24/7 live counsel"
- Body: "Connect with a licensed attorney by live video during any law
  enforcement-initiated encounter. Available 24/7 wherever you need us."
- Hero UI text: "Live attorney" badge · "Secure" badge · "You" self-view tile ·
  "Attorney Jordan Hayes / Verified network attorney"
- Buttons: Register · Log in
- Layout: photographic live-call hero (attorney video with LIVE ATTORNEY pill, SECURE
  pill, PIP self-view and a verified-attorney caption) above the copy block.

### Welcome screen 2 — "Ready for the unexpected."
- Eyebrow: "Always ready"
- Body: "Select your incident and instantly connect with a licensed attorney by live
  video. Designed for moments you never plan for."
- Hero UI text: "Attorney network ready / Live support is one tap away" · "Live" ·
  tiles: "Traffic stop", "Questioned", "Domestic", "Traffic accident", "Pedestrian" ·
  "All law enforcement-initiated encounters"
- Buttons: Register · Log in
- Layout: light/cream hero with a status ribbon and a 2-column grid of gold incident
  tiles, then the copy block.

### Welcome screen 3 — "Meet Your Legal First Responder."
- Eyebrow: "The experience behind the button"
- Body: "Connect with a licensed attorney specially trained in de-escalation and
  immediate legal support during law enforcement-initiated encounters."
- Hero UI text: "Legal First Responder / Experienced live counsel"; stat pairs —
  "16 yrs / average experience", "<60 sec / typical connection",
  "De-escalation / trained for tense moments", "Rights / constitutional expertise",
  "24/7 / every day of the year", "50 states / licensed coverage"
- Buttons: Register · Log in
- Layout: attorney-credential hero with a six-cell stat grid, then the copy block.

### Welcome screen 4 — "Built for Your Protection."
- Eyebrow: "Protection tools built in"
- Body: "Attorney Shield combines immediate legal support with built-in features
  designed to help you stay prepared, connected, and protected."
- Hero UI text: rotating tool cards labelled "Cloud recording", "Live GPS",
  "PIN-to-End", "Digital glovebox"; header "Built-in protection"; focus caption
  "Secure cloud recording / Auto-saved every session"
- Rotation copy pairs (from the reference's own script — the caption cycles through all
  four): "Secure cloud recording / Auto-saved every session" · "Live GPS location /
  Shared with trusted contacts" · "PIN-to-End protection / You control when it ends" ·
  "Digital glovebox / Important documents at your fingertips"
- Buttons: Register · Log in
- Layout: stacked/rotating card deck hero with a progress-dot row and a live caption,
  then the copy block.

### Welcome screen 5 — "Support Beyond the Encounter."
- Eyebrow: "Member Protection Warranty"
- Body: "Our Member Protection Warranty helps reimburse qualifying expenses from covered
  law enforcement-initiated encounters."
- Hero UI text: "Attorney Shield · Member example" · "$150.00 reimbursement" ·
  "Approved" · "Example qualifying fee reimbursement" · "Member Protection Warranty
  $150.00" · "Example eligible reimbursement" · disclaimer "Illustrative benefit
  example / Not an in-app claim or payment screen · Terms apply"
- Buttons: Register · Log in
- Layout: mock reimbursement receipt/statement hero with an approved stamp and an
  explicit "illustrative only" info note, then the copy block.

### Welcome screen 6 — "Legal Support, Nationwide."
- Eyebrow: "Wherever you are"
- Body: "Wherever you are in the United States, Attorney Shield helps ensure a licensed
  attorney is only a tap away during law enforcement-initiated encounters."
- Hero UI text: "24/7/365 / Live attorney access" · "50 states / Nationwide network"
- Buttons: Register · Log in
- Layout: US map hero with animated activity lights (26 fixed map coordinates, 5 lights,
  random 1.9–2.9 s fades) and two stat pills, then the copy block.

## Web screens shown inside the Stage 1 section (browser-chrome frames, `attorney-shield.com`)

These four are the plan/payment/handoff screens. They carry web browser chrome, but the
section they sit in is headed "Stage 1 · App Entry / Native App" — see Discrepancies.

### 04 — Choose plan  (web)
- Note: "Each card shows its inclusions up front. Family covers up to 5 (base 3 + up to
  2 added); the stepper only adds above the base of 3 and shows total members on the
  plan. The 7-Day Limited Trial stays visually distinct."
- Screen text: `SCROLLS` indicator · `9:41` · URL `attorney-shield.com` ·
  "Choose your plan" · segmented "Monthly / Semiannual / Annual" ·
  **FreedomPlus** "$16/mo" [Select] — "✓ 1 member", "✓ 24/7 live attorney access",
  "✓ $1,000 Member Protection Warranty", "✓ Secure document vault" ·
  "Best for families" **FreedomFAMILY** "$38/mo" [Select] — "✓ Everything in
  FreedomPlus", "✓ Covers up to 5 members", "✓ Shared family protection";
  "Members on plan / Includes 3 · add up to 2 more" with a `– 3 +` stepper ·
  "Try it free" **7-Day Limited Trial** "$0 due today" [Select] — "✓ Full app access
  for 7 days", "✓ Try the AI demo", "✓ Card required · cancel anytime"
- Layout: scrolling web page, billing-period segmented control, three stacked plan
  cards with inclusion checklists and per-card Select; the family card embeds a member
  stepper; the trial card is visually distinct.
- Applies to: all three user types (entry point; trial card branches to B1, guests
  arrive here from G3 "See plans").

### 05 — Checkout  (web)
- Note: "Stripe payment with the promo confirmation carried by the price line: the plan
  price crosses out and the discounted price sits beside it in green, and the Pay button
  charges the discounted amount. Per Round 4 the code field stays the standard input
  with Apply, so members can try a different code if the first fails; the prototype
  confirms a successful code through the price itself. Auto-renew stays fully disclosed."
- Screen text: "Checkout" · "FreedomFAMILY · Semiannual · ~~$228~~ $205.20" ·
  "Card number / 1234 1234 1234 1234" · "Expiry / MM/YY" · "CVC / •••" ·
  "Promo / gift code" placeholder "Optional" + [Apply] ·
  "Discount applies to initial purchase only. Auto-renews every 6 months at $228 until
  canceled. You can cancel anytime in the app." ·
  checkbox "I agree to the Attorney Shield & Law Firm Terms of Service" "(tap to read)" ·
  [Pay $205.20] · "Secured by Stripe"
- Layout: single-column Stripe-style form; price line at top carries the strikethrough +
  green discounted price; disclosure block above the terms checkbox; full-width gold pay
  button.

### 06 — Payment confirmation  (web)
- Note: "Confirmation for a percentage promo: Paid today (green) and Renewal rate replace
  the single Price line so members never mistake the discount for the ongoing rate. Dev
  note from Attorney Shield: this dual display applies to percentage codes only; BOGO
  codes extend the renewal date instead and keep the single price."
- Screen text: "You're covered." · "Payment confirmed" · "Plan / FreedomFAMILY" ·
  "Members / You + 3" · "Paid today / $205.20" · "Renewal rate / $228 / 6 mo" ·
  "Renews / Dec 24, 2026" · [Return to app]
- Layout: success mark, headline, key/value receipt rows, one primary return action.

### 07 — Return to app  (web) — **App ↔ Web handoff**
- Note: "A deep link hands the member back to the app automatically, email pre-filled.
  The manual fallback keeps a continuity icon beside it, but it is a muted, non-tappable
  app glyph — not the external-link arrow — so members do not mistake it for a link out."
- Screen text: "Taking you back / to the app…" · "Your account is ready. We'll pre-fill
  your email automatically." · [Open app manually]
- Layout: centred transitional/handoff state with a spinner-style hero and a single
  muted fallback action.

---

# Stage 4 · In-App Registration Completion — badge "Native App"

Hint: "↔ Swipe through all five in-app steps".
Shared guidance pattern (from screen 08's note): "Step screens 08 through 12 now share
one guidance system: the sub-line carries the instruction only, and a steel-blue info
chip below it carries what the information is used for. Always visible, no tap to
reveal, visually subordinate to the fields. This is the proposed pattern for the
consistency question."

### 08 — Enter phone number  · tag "Progress bar starts"
- Screen text: "Step 1 of 5 · Finish setup" · "Enter your phone number" ·
  "We'll text a code to verify it." · info chip: "Your number routes the attorney
  callback if a call ever drops, and secures your account. Never used for marketing." ·
  "Mobile number" `+1` "(555) 000-0000" · [Send code]
- Layout: step label + progress bar, title, instruction sub-line, steel info chip, one
  country-code + number field, primary gold button.

### 09 — Verify phone  · tag "Progress bar starts"
- Note: "The 6-digit SMS code confirms the mobile number entered on the previous screen."
- Screen text: "Step 2 of 5 · Finish setup" · "Verify your phone" · "We use this to route
  your callback and to log you in faster next time." · info chip: "Confirms this phone is
  really yours, so only you can reach your attorney line." · code entry "81————" ·
  [Verify number] · "Didn't get it? Resend code"
- Layout: 6-cell OTP entry with two cells filled, primary verify button, resend link.

### 10 — Personal details
- Note: "Date of birth, gender, and pronouns — collected now that payment is done."
- Screen text: "Step 3 of 5" · "A few personal details" · "Must match your legal ID so an
  attorney can represent you properly in an encounter." · "Date of birth / MM / DD /
  YYYY" · "Gender / Select ▾" · "Pronouns / Select ▾" · [Continue]
- Layout: three-part DOB field row plus two select dropdowns, primary continue.

### 11 — Address
- Note: "Physical address with a 'mailing is the same' checkbox. A note explains it's for
  welcome-packet delivery."
- Screen text: "Step 4 of 5" · "Your address" · "Used to ship your welcome packet." ·
  info chip: "Gives your attorney your home jurisdiction for context. Coverage is never
  affected; you are protected in all 50 states." · "Street address / 123 Main St" ·
  "City / City" · "ZIP / 00000" · checkbox "Mailing address is the same" · [Continue]
- Layout: stacked address fields with City/ZIP paired, checkbox, primary continue.

### 12 — Security PIN  · tag "→ Home"
- Note: "A 4-digit PIN with confirm. Copy explains its real purpose: it ends a live
  session securely and prevents accidental disconnection — it does not unlock the app or
  protect recordings. Confirming the PIN completes setup and lands the member directly
  on the home screen (see The Member App)."
- Screen text: "Step 5 of 5" · "Create a security PIN" · "Used to end a live session
  securely and prevent accidental disconnection. Set it, then re-enter to confirm." ·
  info chip: "The PIN has one job: ending a live session securely. It never locks the app
  or your account." · numeric keypad "1234567890⌫"
- Layout: 4-dot PIN indicator over a custom numeric keypad with backspace.

---

# Stage 5 · Post-Registration Guided Completion — badge "Native App"

Hint: "↔ Swipe through the full completion flow — checklist, documents, contacts, and
tour". Rendered as two horizontally scrolling rows (13→15, then 16→21).

### 13 — Guided completion
- Note: "Reached from the home screen or a nudge. Checklist items are single-line for even
  heights and aligned Add/View buttons. If new document types ship later, the completion
  percentage recalculates downward, the new section appears as addable, and 'Mark
  documents as complete' unchecks automatically so members re-confirm."
- Screen text: "You're all set — finish your profile" · "75% COMPLETE" · "A few quick
  steps make you fully protected." · rows: "Account created" (done) ·
  "Set a password [Add ›]" · "Upload documents [View ›]" · "Add emergency contacts
  [Add ›]" · "Common situations [Add ›]" · [Continue setup] ·
  "Skip for now — go to home"
- Layout: percentage ring/bar header, single-line checklist rows with right-aligned
  Add/View actions, primary continue, plain skip link.

### 13A — Set a password  · tag "New"
- Note: "Opened from the setup checklist. Live requirement checks flip green as they pass;
  the info chip reminds members the one-time code path always works. Saving marks the
  checklist item complete and recalculates readiness."
- Screen text: "Set a password" · "New password ••••••••••" · "Confirm password
  ••••••••••" · rules "At least 8 characters", "At least 1 number", "At least 1 symbol" ·
  info chip: "A password makes sign-in faster on this device. You can always sign in with
  a one-time text code instead." · [Save password]
- Layout: two masked fields, live-validating requirement list, info chip, primary save.

### 13B — Home · situations saved
- Note: "The standard home screen, identical to the member home (27) for an activated
  account and to the guest home (G2) for a guest, with no special guided treatment
  layered on. The three situation slots sit one tap from the attorney button, empty until
  the member fills them. A small underlined Change link sits beside the section heading so
  members can tell the set is editable at any time; it opens the common situations page,
  where any situations already chosen come up pre-selected so they can be swapped."
- Screen text: `SCROLLS` · "ATTORNEY SHIELD" + bell badge "2" · "WELCOME BACK" ·
  "Protected, Jesse" · "Active · 24/7 coverage" · hero "Connect to an attorney / Tap for
  live legal help — any time" · "Your most common situations" + "Change" ·
  three "Add situation" placeholders · readiness card "✕ 80% Protection readiness / Add
  emergency contacts to be fully ready ›" · tab bar "Home / Glovebox / Activity / Profile"
- Layout: app bar with bell, welcome + status line, gold shield hero button, editable
  3-slot situation row, dismissible readiness card, 4-tab bottom bar.

### 13C — Common situations · select up to three  · tag "New"
- Note: "Opened from the Common situations row on the setup checklist, and again later from
  the Change link on the home screen. The guidance and the reason sit at the top, then the
  full situation list is shown as selectable tiles rather than empty placeholders, so
  members can see every option at once. Up to three can be chosen; the fourth tap is
  ignored until one is released. To swap a situation, tap a selected tile to remove it and
  then pick another. Arriving from Change shows the current three already selected.
  Progress is phrased as how many items are left rather than a fixed step number, so it
  reads correctly whichever order the member completes the checklist in. The body scrolls
  so the full list stays at full size."
- Screen text: `SCROLLS` · "Common situations" · "2 more to finish your profile" ·
  "Add your common situations" · "Pick the situations you're most likely to face. Saving
  them now means one tap connects you to the right attorney the moment it counts." ·
  "Choose up to three. They stay one tap from home." · tiles: "Traffic Stop ✓",
  "Pedestrian ✓", "Auto ✓", "At Home ✓", "Domestic ✓", "Other ✓" ·
  "Tap to select up to three. To swap one out, tap it again to remove it, then pick
  another." · [Done] · "Skip for now"
- Layout: scrolling picker; heading + rationale, 2-column selectable tile grid with gold
  checkmarks, helper line, Done + skip.

### 14 — Upload documents  · tag "New"
- Note: "Opened from the checklist. The same Glovebox the member uses later (see The Member
  App) — driver's, health, gun, citizenship with saved / not-added status. The member can
  mark the step complete even with a partial upload; Done returns to the checklist with the
  box checked."
- Screen text: "Finish your profile" · "Upload documents" · "Stored in your Glovebox ·
  shareable with your Law Firm Representative during a call" · "Encrypted Glovebox /
  2 more documents to add / Add the rest any time — or mark this step complete below." ·
  rows "Driver's Information ● Saved [View]", "Health Information ● Saved [View]",
  "Gun Information Not added [Add]", "Citizenship Info Not added [Add]" ·
  checkbox "Mark documents as complete" · [Done — back to checklist]
- Layout: summary status card, four document rows with status pill + action, completion
  checkbox, primary done.

### 14A — Inside a document section · viewing  · tag "New"
- Note: "What a member sees inside any of the four Glovebox sections once saved, Driver's
  Information shown: masked sensitive values, plain rows, photo status, one Edit action.
  The same template serves Health, Gun Information, and Citizenship Info for consistency."
- Screen text: "Driver's Information" · "Encrypted · visible to your attorney during
  calls" · "License number / •••• •••• 4821" · "State / New York" · "Expiration / 03 /
  2029" · file tiles "drivers-license-front.jpg / 1.8 MB · uploaded Jun 30 ✕" and
  "drivers-license-back.jpg / 1.6 MB · uploaded Jun 30 ✕" · "+ Add another document" ·
  [Camera] [Gallery] · [Save changes]
- Layout: section title + encryption sub-line, field rows, uploaded document tiles with
  delete, add-another link, Camera/Gallery capture pair, primary save.

### 14B — Health Information · section  · tag "New"
- Note: "The health section pairs three plain fields with the shared upload pattern: drag
  and drop (tap on device), plus Camera and Gallery capture paths on mobile. The faded
  cross-and-pulse motif marks the section without competing with content. Save Changes
  commits fields and files together."
- Screen text: "Health Information" · "Encrypted · visible to your attorney during calls" ·
  "Medical conditions / Asthma; penicillin allergy" · "Mental health conditions / None
  listed" · "Prescribed medications / Albuterol inhaler · 90mcg" · dropzone "Upload
  document / Insurance card, medication list, PDF or photo" · [Camera] [Gallery] ·
  [Save changes]
- Layout: same template as 14A but in the empty-dropzone state; faded cross-and-pulse
  watermark motif.

### 14C — Gun Information · section  · tag "New"
- Note: "Two yes/no questions (tappable on the board), permit number and issue state, and
  the shared upload pattern shown in its uploaded state: the dropzone is replaced by a
  document tile with a thumbnail, filename, and delete, with Add Another Document beneath.
  Deleting the last file restores the dropzone. The faded rings motif is this section's
  mark."
- Screen text: "Gun Information" · "Encrypted · visible to your attorney during calls" ·
  "Are you a gun owner? [Yes] [No]" · "Concealed carry permit? [Yes] [No]" ·
  "Permit number / CC-48291" · "Issue state / New Jersey" ·
  "carry-permit-front.jpg / 1.2 MB · uploaded just now ✕" · "+ Add another document" ·
  [Camera] [Gallery] · [Save changes]
- Layout: yes/no segmented rows, two fields, uploaded tile state, capture pair, save.

### 14D — Citizenship Info · section  · tag "New"
- Note: "This screen scrolls (see the side indicator): content sits at its natural size and
  the member scrolls to Save. Passport number, a working issued-in state selector (tap it
  on the board), visa number, and additional information, with two separate upload slots:
  the passport shown uploaded as a tile, the birth certificate still an empty dropzone, so
  both states read side by side. Globe-and-stamp motif, faded."
- Screen text: `SCROLLS` · "Citizenship Info" · "Encrypted · visible to your attorney
  during calls" · "Passport number / •••• 88412" · "Issued in / New Jersey" with open
  option list "New Jersey / New York / California / Texas / Florida / Pennsylvania" ·
  "Visa number / Not applicable" · "Additional information / Dual citizenship: none" ·
  "Passport" → "passport-photo-page.jpg / 2.4 MB · uploaded Jun 30 ✕" ·
  "+ Add another document" · "Birth certificate" → dropzone "Upload document / PDF or
  photo of your birth certificate" · [Camera] [Gallery] · [Save changes]
- Layout: scrolling form with an open state-select dropdown and two labelled upload slots
  showing filled and empty states side by side.

### 15 — In-app nudges
- Note: "A non-blocking prompt over the home screen. 'Add now' opens the contact form
  (next); 'Later' dismisses — and on first launch the quick tour follows. Paired with
  automated email reminders. Timing per Round 4: this nudge appears after the member has
  added their common situations — situations first, then the nudge asking for emergency
  contacts."
- Screen text: full home screen (app bar + bell "2", "WELCOME BACK / Protected, Jesse",
  "Active · 24/7 coverage", hero "Connect to an attorney / Tap for live legal help — any
  time", "Your most common situations / Traffic Stop / Pedestrian / Auto", readiness card
  "✕ 80% Protection readiness / Add emergency contacts to be fully ready ›", tab bar) ·
  overlay: "Add an emergency contact" / "They're alerted with your location during any
  encounter." / [Add now] [Later]
- Layout: dimmed home screen with a non-blocking card overlay carrying two actions.

### 16 — Add contact · from 'Add now'  · tag "New"
- Note: "Opened from 'Add now' on the nudge or the checklist: first and last name, mobile,
  email, relationship, and notify-by checkboxes so alerts can go to text, email, or both."
- Screen text: "Emergency contacts" · "Add an emergency contact" · "They're alerted with
  your location the moment you connect to an attorney." · "First name / Jordan" ·
  "Last name / Avery" · "Mobile number / +1 / (555) 000-0000" · "Email /
  jordan@email.com" · "Notify them by / Text message / Email / Choose one or both" ·
  "Relationship / Spouse / Parent / Friend / Other" · [Save contact] · [Cancel]
- Layout: form with name pair, phone, email, two notify checkboxes, relationship chip row,
  save + cancel.

### 17 — Guided walkthrough  · tags "New members · first launch"
- Note: "First launch, new members only. The background blurs and dims while the focused
  element is lifted above it, highlighted in gold with a pulsing ring, so there is never a
  question of what the tour is pointing at. Step 1 spotlights the attorney shield."
- Screen text: home screen behind + "Quick tour · 1 of 4" · "Skip tour" ·
  "This is your lifeline." · "Tap the shield any time you're in contact with law
  enforcement to reach a licensed attorney live." · [Next] ·
  "Replay anytime from Settings"
- Layout: blurred/dimmed home with the shield cloned above it inside a pulsing gold ring,
  plus a coach-mark card with step counter, Skip, and Next.
- Applies to: new members, first launch only.

### 18 — Tour · step 2  · tags "New · → Home"
- Note: "Tapping 'Next' moves through the remaining steps (Glovebox, Activity,
  notifications). 'Skip tour' at any point — or finishing — lands the member on the home
  screen."
- Screen text: "Quick tour · 2 of 4" · "Skip tour" · "Your Glovebox, always ready." ·
  "Keep your driver's, health and other documents here — your attorney sees them the
  moment you connect." · [Next] · "Replay anytime from Settings"
- Layout: same spotlight pattern, focus on the Glovebox tab.

### 19 — Tour · step 3  · tag "New"
- Note: "Step 3 highlights Activity: recordings and transcripts of every session, saved
  automatically."
- Screen text: "Quick tour · 3 of 4" · "Skip tour" · "Every call, on the record." ·
  "Recordings and transcripts of every session are saved automatically in Activity — your
  evidence, kept safe." · [Next] · "Replay anytime from Settings"
- Layout: same spotlight pattern, focus on the Activity tab.

### 20 — Tour · step 4  · tag "New"
- Note: "The final step covers notifications and control. 'Finish' leads to the
  congratulations screen."
- Screen text: "Quick tour · 4 of 4" · "Skip tour" · "You're in control." · "A quiet bell
  collects reminders and tips. Tune or silence every notification any time in Settings." ·
  [Finish] · "Replay anytime from Settings"
- Layout: same spotlight pattern, focus on the bell; primary action becomes Finish.

### 21 — Tour complete · congratulations  · tags "New · → Home"
- Note: "A celebratory close in the same visual language as the tour, with an animated gold
  flash pulsing around the card. One action: Go to Home Screen."
- Screen text: "Tour complete" · "Congratulations — you're ready." · "You know your way
  around. Your attorney is one tap away — any time, day or night." ·
  [Go to Home Screen]
- Layout: centred celebration card over the blurred home, animated gold flash, single
  primary action.

---

# Branch flow B1 · from screen 04 — "The 7-Day Limited Trial — signup" — badge "Native App"

Hint: "↔ Choosing the trial on Choose Plans: plan-conversion popup → trial checkout →
confirmation → back to the app". Applies to: **7-Day Limited Trial** user type.

### V1 — 7-Day Limited Trial card  (web) · tag "7-Day Limited Trial"
- Note: "Same checkout flow, distinct card. Clear messaging: card required, $0 due today,
  cancel anytime — visually distinct from the paid plans. 'Start trial' leads into the
  sequence to the right."
- Screen text: "Choose your plan" · "FreedomPlus $16/mo" · "FreedomFAMILY $38/mo" ·
  "★ Limited Trial" · "7-Day Limited Trial" · "$0 due today" · "Card required · cancel
  anytime · full app access for 7 days" · [Start trial]
- Layout: the 04 plan page with the trial card promoted/expanded and starred.

### T1 — Trial · choose conversion plan  (web) · tag "7-Day Limited Trial"
- Note: "After 'Start trial,' the member chooses their trial plan. This is the plan they are
  on during the trial and the plan that continues if it converts. Selecting FreedomFAMILY
  expands the card inline with a sub-account stepper: starts at 0 additional (base includes
  3), add up to 2 more, minus disabled at zero."
- Screen text (checkout page behind): "Checkout" · "FreedomFAMILY · Semiannual · $228" ·
  card/expiry/CVC fields · "Promo / gift code Optional [Apply]" · "Discount applies to
  initial purchase only. Auto-renews every 6 months at $228 until canceled. You can cancel
  anytime in the app." · terms checkbox · [Pay $228] · "Secured by Stripe" ·
  overlay popup: "7-Day Limited Trial" · "Choose your trial plan" · "$0 due today. This is
  your plan during the trial, and the plan you stay on if you don't cancel before the 7
  days end." · "FreedomPlus / 1 member / $16/mo" · "FreedomFAMILY / You + up to 4 members
  / $38/mo" · "Additional sub-accounts / Base plan includes 3 members · add up to 2 more"
  with `− 0 +` stepper · [Continue]
- Layout: plan-conversion modal over the checkout page; two selectable plan rows, the
  family row expanding to reveal the sub-account stepper.

### T2 — Trial checkout  (web) · tag "Replaces discount language"
- Note: "The trial checkout: card on file, $0 due today, explicit conversion terms. No promo
  or gift code field — promos do not apply to the trial."
- Screen text: "Checkout" · "7-Day Limited Trial · FreedomFAMILY plan" ·
  "Card number / 1234 1234 1234 1234" · "Expiry / MM/YY" · "CVC / •••" ·
  "After your 7-day limited trial ends, your card will be charged the full amount of your
  selected plan — FreedomFAMILY at $38/mo. Cancel anytime in the app before then and you
  won't be charged." · terms checkbox "I agree to the Attorney Shield & Law Firm Terms of
  Service (tap to read)" · [Start trial — $0 due today] · "Secured by Stripe"
- Layout: same checkout shell as 05, promo field removed, conversion disclosure in its
  place.

### T3 — Trial confirmation  (web) · tag "FreedomFAMILY shown"
- Note: "Mirrors the payment confirmation (screen 06), shown here with FreedomFAMILY
  selected: the plan it converts to, members, the exact trial end date, and the amount
  charged after."
- Screen text: "Your trial is active." · "$0 charged today" · "Plan after trial /
  FreedomFAMILY" · "Members / You + up to 4" · "Trial ends / Jul 10, 2026" ·
  "Then / $38 / mo" · [Return to app]
- Layout: same receipt pattern as 06 with trial-specific rows.

### T4 — Return to app · same as 07  (web) — **App ↔ Web handoff**
- Note: "A deep link hands the member back to the app, email pre-filled. Planned: this
  screen will branch by origin — app-initiated signups continue through the deep link,
  while website-mobile signups will see App Store / Google Play badges plus an 'Open the
  app' option. The layout reserves space for both states."
- Screen text: "Taking you back / to the app…" · "Your account is ready. We'll pre-fill
  your email automatically." · [Open app manually]
- Layout: identical to 07, with reserved space for the future store-badge variant.

---

# Branch flow B2 · 7-Day Limited Trial, in-app — "When a trial member taps to connect" — badge "Native App"

Hint: "↔ Triggered when a trial member taps any attorney tile or the hero shield on Home —
the gate, the charge notice, card processing, and full activation".

**Structural note:** this single horizontally scrolling row also contains the guest screens
(G1–G3) and the whole member app (27–35). The document references "The Member App" in prose
but renders no separate section header for it.

## Trial gate and conversion (7-Day Limited Trial user type)

### V2 — Trial: attorney button  · tag "7-Day Limited Trial"
- Note: "Tapping any attorney tile or the hero shield while on a trial opens this gate. Two
  choices: 'Start Membership to Connect Live' (leads to the charge confirmation, next) or
  the free guided AI demo."
- Screen text: "Home" · "You're on a Trial" · "Live attorney access starts your paid
  membership. Or try a guided demo first — free." · [Start Membership to Connect Live] ·
  [Try the AI demo instead] · "Requesting live support charges your card and begins
  membership immediately."
- Layout: full-screen/overlay gate with a headline, two stacked actions, fine-print
  disclosure.

### T5 — Charge notice · FreedomPlus  · tag "$16/mo"
- Note: "Tapping 'Start Membership to Connect Live' shows this clear notice: the exact plan
  and price about to be charged to the card on file. This is the FreedomPlus version."
- Screen text: home screen behind · overlay "Card on file" · "Start your membership now?" ·
  "Your 7-day trial ends and your card on file is charged today. Live attorney access
  unlocks immediately." · "FreedomPlus $16/mo" · "1 member · billed monthly · cancel
  anytime" · [Yes, charge my card] · [Not now] · "Secured by Stripe · Visa ending 4242"
- Layout: bottom sheet over home with plan summary row, confirm/decline pair, Stripe
  reassurance line.

### T6 — Charge notice · FreedomFAMILY  · tag "$38/mo"
- Note: "The same notice for FreedomFAMILY members — identical structure, different plan and
  price. 'Yes, charge my card' leads to processing."
- Screen text: as T5 but "FreedomFAMILY $38/mo" · "You + up to 4 members · billed monthly ·
  cancel anytime"
- Layout: identical to T5.

### T7 — Processing payment  · tag "Status bar"
- Note: "A calm holding state with a status bar while the card on file is charged. No dead
  ends — it resolves to the confirmation."
- Screen text: "Processing your card / on file…" · "Confirming with Stripe — this takes a
  few seconds." · "Visa ending 4242 · Don't close the app"
- Layout: centred processing state with an indeterminate progress bar and a do-not-close
  caption.

### T8 — Payment confirmed · like 06  · tag "FreedomFAMILY shown"
- Note: "The same confirmation pattern as screen 06 — plan, members, price, start date —
  now inside the app."
- Screen text: "You're covered." · "Membership active — payment confirmed" ·
  "Plan / FreedomFAMILY" · "Members / You + up to 4" · "Price / $38 / mo" ·
  "Started / Jul 3, 2026" · [Connect to legal support now] · [Go to home]
- Layout: in-app version of the 06 receipt with two actions (connect now, or home).

## Guest flow (Guest user type)

### G1 — Guest entry · unrecognized email  · tag "New"
- Note: "When Log In gets an email with no account, the app offers the path forward: start a
  membership, retry, or continue as a guest with first name, last name, and the email
  already entered. Guests understand the limits before they enter."
- Screen text: "Sign in" · "We couldn't find that email" · "jordan@email.com isn't linked to
  a membership yet." · [Start a membership] · [Try a different email] · "or" ·
  "Continue as a guest" · "Explore the app. Live attorney access requires a membership or
  trial." · "First name / Jordan" · "Last name / Avery" · [Continue as guest]
- Layout: error/branch screen with two primary paths, an "or" divider, then a small guest
  form.

### G2 — Guest home · logged in as guest  · tag "New"
- Note: "Guests land on the real home: same shield, same layout, honest status pill. The one
  difference is behavioral: tapping the shield, a situation tile, or any member feature
  opens the membership gate (G3) instead of the connect flow. The product sells itself by
  being usable, not by being hidden."
- Screen text: "ATTORNEY SHIELD" + bell "2" · "Exploring as guest" · "Jordan Avery" ·
  "Guest access · live attorney help requires a membership" · hero "Connect to an attorney /
  Tap for live legal help — any time" · "Your most common situations" · three "Add
  situation" placeholders · readiness card "✕ 80% Protection readiness / Add emergency
  contacts to be fully ready ›" · tab bar "Home / Glovebox / Activity / Profile"
- Layout: identical to member home 27, with the status line replaced by a guest pill.

### G3 — Guest gate · restricted feature  · tag "New"
- Note: "Opens over the guest home (G2) whenever a guest taps the shield, a situation tile,
  or any member feature: what is locked, why, and two honest paths in. Calm, never punitive;
  Not now returns to browsing. Routing: Start 7-Day Limited Trial opens the trial card (V1);
  See plans opens Choose your plan (04)."
- Screen text: "This feature needs a membership" · "Live attorney access, the Digital
  Glovebox, and secure recordings are for members. Start a 7-Day Limited Trial to unlock
  everything." · [Start 7-Day Limited Trial] · [See plans] · [Not now]
- Layout: centred gate sheet with two upgrade paths and a plain dismiss.

## The Member App (screens 27–35, no separate section header)

### 27 — Home · the guardian  · tag "Redesigned"
- Note: "Home for a new member: the three most-common slots start as dashed Add-a-situation
  placeholders so members choose their own and see every incident type at least once (in the
  picker). Filled during post-registration setup or by tapping any placeholder. Dismissing
  the readiness card shifts the tiles down and scales the attorney button up — the tiles
  never grow."
- Screen text: "ATTORNEY SHIELD" + bell "2" · "WELCOME BACK" · "Protected, Jesse" ·
  "Active · 24/7 coverage" · hero "Connect to an attorney / Tap for live legal help — any
  time" · "Your most common situations" · three "Add situation" placeholders ·
  readiness card "✕ 80% Protection readiness / Add emergency contacts to be fully ready ›" ·
  tab bar "Home / Glovebox / Activity / Profile"
- Layout: as 13B, in its empty-slot state; the gold shield hero is the dominant element.

### 27B — Hold a tile · customize your three  · tag "New"
- Note: "Opened by tapping an empty placeholder, holding a filled tile, or from the setup
  checklist: all six situations, choose up to three, Done writes them to home. Same glow and
  neon-blue selection language, gold check on chosen tiles."
- Screen text (tray screen behind): "ATTORNEY SHIELD" · "Protected · 24/7" · "Tap your
  situation" · tiles "Test Call / Traffic Stop / Auto Accident / Pedestrian Stop / Domestic
  / Other" · tab bar · overlay: "Your most common situations" · "Choose up to three. They
  stay one tap from home." · tiles "Traffic Stop ✓ / Pedestrian ✓ / Auto ✓ / At Home ✓ /
  Domestic ✓ / Other ✓" · [Done]
- Layout: selection sheet over the incident tray; 2-column tile grid, gold checks, single
  Done.

### 27A — Golden shield · choose & connect  · tag "New"
- Note: "Path 1 of two connect paths: tapping the attorney shield opens the full tray of
  incident types as glass tiles. Tapping an incident is the action itself: it flashes as a
  button press and connects directly to an LFR. No selection state, no checkmark, no extra
  confirmation. Cancel sits at the bottom."
- Screen text: "ATTORNEY SHIELD" · "Protected · 24/7" · "Tap your situation" · tray tiles
  "Test Call / Traffic Stop / Auto Accident / Pedestrian Stop / Domestic / Other" · tab bar ·
  "Connect to an attorney now?" · "A licensed attorney joins your call live" · "Secure cloud
  recording begins automatically" · "What's happening?" · tiles "Traffic Stop / Pedestrian /
  Auto / At Home / Domestic / Other" · [Cancel]
- Layout: full-height glass tile tray with two reassurance lines and a bottom Cancel; tiles
  are direct actions (press-flash, no selected state).

### 28 — Connect confirmation  · tag "Redesigned"
- Note: "Path 2: tapping a saved most-common tile from home lands here — the selected
  incident with a single Connect Now button. The confirmation exists only on this path, to
  prevent accidental connections from the home screen."
- Screen text: tray behind · "Traffic Stop" · "Connect to an attorney now?" · "A licensed
  attorney joins your call live" · "Secure cloud recording begins automatically" ·
  [Connect now] · [Cancel]
- Layout: confirmation sheet naming the chosen incident, two reassurance lines, one primary
  connect and a Cancel.

### 29 — Connecting  · tag "New"
- Note: "While connecting, rotating tips cycle in the gold card (final copy from Attorney
  Shield) with progress dots; the encrypted-and-recording line stays fixed. Blue Sky endorses
  the rotating tips with two guardrails: tips stay calm and practical (never marketing), and
  the rotation pauses under reduced motion."
- Screen text: "Connecting you / to an attorney" · "Securely reaching the next available
  counsel. Stay on this screen." · "WHILE YOU WAIT" · "Keep your phone steady and let the
  attorney see what's happening." · "Encrypted · recording starts when connected" · [Cancel]
- Rotating tip copy (all three, from the reference's own script, 4 s interval):
  1. "Keep your phone steady and let the attorney see what's happening."
  2. "You can say: I'm exercising my right to remain silent."
  3. "Your emergency contacts have been alerted with your location."
- Layout: centred connecting state, gold tip card with progress dots, fixed encryption line,
  Cancel.

### 30 — Live connection  · tag "Redesigned"
- Note: "Matches the real call: attorney video, verified header, timer, REC, self-view.
  Documents opens the simplified in-call sheet (30A), not the full Glovebox. End requires the
  PIN."
- Screen text: "Attorney video" · "Rachel Whitmore" · "Attorney Shield counsel · connected" ·
  "17:32" · "REC" · "You" · [Documents] [Mute] [Flip] [End]
- Layout: full-bleed attorney video, verified header with timer + REC badge, PIP self-view,
  four-action control bar.

### 30A — In-call documents · simplified  · tag "New"
- Note: "Tapping Documents during a live call opens this lightweight sheet: every saved
  document is automatically visible to the LFR, so rows carry View, not share controls. Empty
  categories show as dashed placeholders. The call header and REC stay visible; access ends
  with the call."
- Screen text: "Rachel Whitmore · 02:47" · "● REC" · "Share a document" · "Everything saved
  here is visible to your attorney during the call. Access ends when the call ends." ·
  "Driver's Information [View]" · "Health Information [View]" · "Gun Information / Nothing
  uploaded yet / Empty" · "Citizenship Info [View]" · [Back to call]
- Layout: sheet under a persistent call header; four document rows, dashed empty state, back
  action.

### 31 — Digital Glovebox · documents  · tag "Redesigned"
- Note: "Documents reframed as the Digital Glovebox — the marketing term members already know,
  with 'Glovebox' fitting the tab label where 'Vault' fell flat. An encrypted-and-ready summary
  plus clean per-document rows with status, shareable with the Law Firm Representative during a
  call."
- Screen text: "Digital Glovebox" · "Secured · shareable with your Law Firm Representative
  during a call" · "Encrypted & ready / 4 documents on file / Instantly available to your
  attorney the moment you connect." · rows "Driver's Information ● Saved [View]", "Health
  Information ● Saved [View]", "Gun Information Not added [Add]", "Citizenship Info Not added
  [Add]" · tab bar "Home / Glovebox / Activity / Profile"
- Layout: summary status card over four document rows; Glovebox tab active.

### 32 — Activity · timeline  · tag "Redesigned"
- Note: "Timeline of sessions: type, date, duration, attorney. Recording replay is not part of
  the experience — no REC badges, no replay links. Test Call entries keep View transcript, the
  intended way to review demo sessions."
- Screen text: "Activity" · "Traffic Stop / Jun 20, 2026 · 9:14 PM · 4m 12s · Rachel Whitmore" ·
  "Test Call / Jun 12, 2026 · 2:03 PM · 1m 04s · Practice run / View transcript ›" ·
  "You joined Attorney Shield / Jun 1, 2026 · Welcome to full 24/7 protection" · tab bar
- Layout: vertical timeline of session cards, transcript link on test calls only, join event as
  the timeline's origin.

### 33 — Profile · account  · tag "Redesigned"
- Note: "The old flat menu, reorganized: a membership status card (plan, members, renewal,
  coverage) on top, then grouped sections — Account, Protection, More."
- Screen text: `SCROLLS` · "Jesse" · "FreedomFAMILY · Active" · "You + 3 members" · "Covered" ·
  "Renews Dec 24, 2026" · "Manage plan ›" · **Account**: "Profile & personal info", "My
  documents", "Payment & plan" · **Protection**: "Emergency contacts", "PIN & security" ·
  **More**: "Support & intro video"
- Layout: scrolling profile with a membership status card then three grouped row lists.

### 33A — Payment & plan  · tag "New"
- Note: "Everything money: plan summary with renewal and price, payment method, billing history,
  and Family members. Plan changes are not available in-app, so there is no Change plan row.
  Delete account (App Store required wording) is the one red action on the screen."
- Screen text: "Payment & plan" · "FreedomFAMILY · Semiannual" · "$38/mo · You + 3 members" ·
  "$228" · "Renews Dec 24, 2026" · "● Covered" · "Payment method / Visa •••• 4242 · expires
  08/28 [Update ›]" · "Family members / 3 of 5 on your plan [Manage ›]" · "Billing history /
  Receipts and past payments [View ›]" · "Delete account"
- Layout: plan summary card then three navigation rows, with a single red destructive row at the
  bottom.

### 33B — Family members · sub-accounts  · tag "New"
- Note: "Sub-accounts only; the primary account never appears here. Filled cards show green
  Active status and pending cards say Invite sent with a gold Resend action. Per Round 4, empty
  slots mirror the member cards as closely as possible: the same card layout with a dashed
  outline, a ghost profile avatar, Open member spot, Included in your plan, and a gold Invite
  action — so remaining capacity reads as real spots waiting to be filled rather than a generic
  add button."
- Screen text: "Family members" · "2 of 4 sub-accounts added. Your FreedomFAMILY plan covers you
  plus up to 4 members." · "T / Taylor Avery / Joined Jun 2026 / Active" ·
  "M / Morgan Avery / Invite sent / Resend" · "Open member spot / Included in your plan /
  Invite" ×2 · "Each member gets their own account with full protection. Adding a member asks for
  first name, last name, and email, and sends an invite."
- Layout: four uniform member cards — two filled (active, pending), two dashed empty spots — plus
  an explanatory footer.

### 33C — Settings  · tag "New"
- Note: "The five current settings, one row each. Push notifications opens the existing
  notification settings screen (26), never a duplicate. Delete account intentionally lives in
  Payment & plan only."
- Screen text: "Settings" · "Change password / Update your sign-in password [Update ›]" ·
  "Language / English (US) [Change ›]" · "Push notifications / Nudges, renewals, and alerts
  [Manage ›]" · "Device permissions / Camera · Microphone · Location [Review ›]" ·
  "Terms of Service / Attorney Shield and Law Firm, combined [View ›]" ·
  "Delete account lives in Payment & plan"
- Layout: five two-line rows with right-side actions, plus a footnote.

### 33D — Payment method · view & edit  · tag "New"
- Note: "Members see the card on file and edit the fields that actually change, expiration and
  ZIP, inline. Replacing the card is one tap away; nothing requires delete-and-re-add. Reached
  from the Update action on Payment & plan."
- Screen text: "Payment method" · "VISA / Active" · "•••• •••• •••• 4242" · "JESSE D" ·
  "EXP 08/28" · "Expiration / 08 / 28" · "Billing ZIP / 07601" · "Update the expiration date or
  ZIP without re-entering the card. Replacing the card keeps coverage uninterrupted." ·
  [Save changes] · "Replace with a new card ›"
- Layout: card-art preview on top, two editable fields, explanation, save, then a replace link.

### 34 — PIN · end session  · tag "Redesigned"
- Note: "The PIN gate for ending a live session. Dev note: a Forgot PIN option appears only when
  this screen is reached from the Test Call flow; during a real attorney session there is no
  recovery path on this screen by design."
- Screen text: "Enter your PIN" · "Ends a live session securely and prevents accidental
  disconnection." · keypad "1234567890⌫" · "Forgot PIN?"
- Layout: PIN dots over the numeric keypad; conditional Forgot PIN link below.

### 35 — Home · grace & expired states  · tag "State"
- Note: "Grace period: the status bar is a single line in the same format as Active and Expired,
  never a day count. The payment action lives at the bottom as a green Pay now with one plain
  lead-in sentence. The scaled-up attorney button carries continued access on its own; hero copy
  (final wording from Attorney Shield) confirms access continues but is at risk without payment."
- Screen text: `SCROLLS` · "ATTORNEY SHIELD" + bell "2" · "WELCOME BACK" · "Protected, Jesse" ·
  "Grace period - fully covered until 7/24/26 9:41 PM" · hero "Connect to an attorney / Tap for
  live legal help · your access continues through your grace period" · "Your most common
  situations / Traffic Stop / Pedestrian / Auto" · "Your membership is in its grace period.
  Settle your renewal to keep full coverage." · [Pay now] (green) · tab bar
- Layout: home screen with the status line swapped for the grace message, enlarged shield hero,
  and a green Pay now block at the bottom in place of the readiness card.

---

# Section 6 · "Stage 5 · in detail" — The nudge & notification system — badge "Native App"

Intro: "Stage 5's reminders, designed in full. A calm three-layer system — a quiet bell, one
notification center, and the occasional gentle nudge — that gets members fully set up without
ever becoming the kind of app people mute. These are ongoing app features, not sign-up steps."

Hint: "↔ Swipe through all five notification screens".

### 22 — Bell · resting  · tag "Updated"
- Note: "The notification entry point on the redesigned guardian home. Resting state: no badge,
  no glow. The bell earns trust by staying quiet when nothing actionable is waiting."
- Screen text: home screen with **no** bell badge — "ATTORNEY SHIELD" · "WELCOME BACK /
  Protected, Jesse" · "Active · 24/7 coverage" · hero · "Your most common situations / Traffic
  Stop / Pedestrian / Auto" · readiness card · tab bar
- Layout: home screen, bell plain.

### 23 — Bell · new nudge  · tag "Updated"
- Note: "Same guardian home, active state: a soft gold glow and a count badge appear when
  actionable items are waiting, so the two bell states read side by side. The badge counts
  actionable unread nudges only."
- Screen text: identical home screen with bell badge "2"
- Layout: home screen, bell with gold glow + count badge.

### 24 — Notification center
- Note: "One calm home for every nudge. Setup items up top with one-tap actions; unread gets a
  subtle gold marker."
- Screen text: "Notifications" · "Mark all read" · **Finish setup**: "Add an emergency contact /
  They're alerted with your location during any encounter. [Add now →]"; "Upload your documents /
  Driver's, health, gun & citizenship info ready when it counts. [Upload →]" · **Earlier**:
  "You're protected / Coverage is active. An attorney is on standby 24/7. / 2 days ago";
  "Tip: know your rights / A 2-minute read for your next traffic stop. / 3 days ago"
- Layout: two grouped lists — actionable setup items with inline actions, then a read-only
  "Earlier" feed with relative timestamps; gold unread markers.

### 25 — Gentle nudge  · tag "Bottom sheet"
- Note: "A non-blocking bottom sheet at a calm moment. 'Maybe later' is the clear centered
  secondary; 'Don't remind me' is fine print; a subtle 'Notification settings' link lets members
  tune nudges without competing with the main action."
- Screen text: "Home" · "Connect to an attorney" · "One quick thing to feel fully covered" ·
  "Add an emergency contact so the people who matter are alerted with your location the moment you
  connect." · [Add a contact] · "Maybe later" · "Don't remind me" · "Notification settings"
- Layout: bottom sheet over home; one gold primary, centred secondary, fine-print opt-out, and a
  settings link.

### 26 — Notification settings
- Note: "Per-category toggles and a frequency dial. Control is the real guarantee against
  annoyance."
- Screen text: "Notifications" · "Choose what you hear about. You're always in control." ·
  "Setup reminders / Finish your profile, documents, contacts" · "Tips & know-your-rights /
  Occasional educational content" · "Account & billing / Renewals, receipts, plan changes" ·
  "Safety-critical / Always on / Coverage lapses & emergency-contact gaps" ·
  "How often / Occasionally | Rarely | Off"
- Layout: four toggle rows (safety-critical locked on) plus a segmented frequency control.

---

# Ground rules — "How the nudges behave" (badge ✦, no env badge)

Intro: "Attorney Shield is an app most members hope to rarely open — which makes a missed setup
step a real safety gap, and one annoying buzz enough to lose the notification channel for good.
The fix is fewer, calmer, genuinely useful nudges, always under the member's control."

1. **Never blocks the app** — "A nudge is always a card you can ignore — never a wall between a
   member and the attorney button."
2. **One at a time, capped** — "At most one nudge per session, never the same one twice. Dismiss
   it and it rests for days."
3. **Timed to calm moments** — "Surfaces after a finished task or a relaxed app open — never
   mid-emergency."
4. **Always says why** — "Leads with the benefit, not the chore. Value first, ask second."
5. **Critical items lean in — gently** — "Safety gaps get a touch more visibility, same soft
   treatment. No red alarms."
6. **Stops when you're done** — "Once setup is complete, the nudges simply end. No streaks, no
   noise."

---

## App ↔ Web handoff — everything the reference says

- Web-chrome frames (browser bar showing `attorney-shield.com`): **04, 05, 06, 07, V1, T1, T2,
  T3, T4**. Every other frame (50 of them) is native app chrome.
- Handoff **out** to web: choosing a plan leaves the native welcome flow for the web plan/checkout
  pages. The reference never draws the outbound transition screen.
- Handoff **back** to app: screens **07** and **T4** — "Taking you back to the app…", deep link
  with email pre-filled, plus a muted, deliberately non-tappable app glyph beside the manual
  "Open app manually" fallback (explicitly *not* an external-link arrow).
- Planned divergence (T4 note): the return screen "will branch by origin — app-initiated signups
  continue through the deep link, while website-mobile signups will see App Store / Google Play
  badges plus an 'Open the app' option. The layout reserves space for both states."
- After the handoff, native registration resumes at **Stage 4 / screen 08**, so payment always
  precedes phone verification, personal details, address, and PIN.

## Payment / paywall steps

- Web: 04 plan choice → 05 Stripe checkout → 06 confirmation → 07 return to app.
- Promo handling: discounted price shown inline (strikethrough + green), Pay button charges the
  discounted amount, code field stays a standard input with Apply so a failed code can be
  retried. Percentage promos get the dual "Paid today / Renewal rate" display; **BOGO codes
  extend the renewal date instead and keep the single price**.
- Auto-renew disclosure is mandatory and unhidden ("Auto-renews every 6 months at $228 until
  canceled. You can cancel anytime in the app.").
- In-app paywall for trials: V2 gate → T5/T6 charge notice (card on file, exact plan + price) →
  T7 processing → T8 confirmation.
- No in-app plan changes: 33A deliberately has no "Change plan" row. Delete account lives only in
  33A (App Store required wording), never in Settings.

## Trial vs guest divergence

- **7-Day Limited Trial**: signs up through the same web checkout but with a distinct card, no
  promo field, $0 due today, card required, and an explicit conversion disclosure. Chooses its
  conversion plan up front (T1). Gets full app access, but tapping the shield or any attorney
  tile hits the V2 gate offering either immediate paid conversion or a free guided AI demo.
- **Guest**: enters through a failed login (G1), lands on the real home with an honest guest pill
  (G2), and every member feature opens the G3 gate. G3 routes to the trial card (V1) or the plan
  page (04). "Not now" always returns to browsing. Guests are never hidden from the UI — "The
  product sells itself by being usable, not by being hidden."
- **Standard Member**: 04 → 05 → 06 → 07 → 08–12 → 13–21, then the member app (27–35).

## In-app nudge system

Three layers: a quiet bell (22/23), one notification center (24), and occasional gentle bottom
sheets (25), all tunable in 26. Nudge instances shown: emergency-contact nudge (15), the
notification-center setup rows (24), and the gentle sheet (25). Timing rule from 15: situations
first, then the emergency-contact nudge. Paired with automated email reminders. Six behavioural
ground rules above.

---

## Explicit component, spacing, radius, and motion specs

These are the concrete values the reference's own stylesheet uses. They describe the web mockup
board, so treat lengths as design-intent ratios rather than iOS points.

### Board / layout
- Content wrapper: `max-width: 1320px`, `padding: 0 28px`.
- Stage phone rows: `display:flex; gap:30px; overflow-x:auto; scroll-snap-type:x proximity`.
- Screen column width: `292px`, `scroll-snap-align:start`.
- Keyboard nav: ← / → scroll the welcome carousel by `min(408px, viewport-22)` when width ≤ 720.

### Phone frame
- Frame: `292 × 600`, radius **38px**, padding `9px`, gradient `#1c2740 → #0b1322`, inner hairline
  `rgba(255,255,255,.07)`, drop shadow `0 30px 60px -28px rgba(0,0,0,.85)`.
- Screen: radius **30px**, background Deep Navy (`--navy3` `#0A1626`); web variant background
  `#0e1c33`.
- Notch: `96 × 22`, bottom radius `0 0 14px 14px`, background `#0b1322`.
- Status bar: height `30px`, padding `9px 18px 0`, font `10px/700`.
- Browser bar (web frames): padding `7px 12px`, background `#0a1626`, 1px bottom hairline.
- Screen body: `padding: 16px 18px`.

### Components
- Chips (masthead): radius `100px`, padding `7px 14px`, `12px/700`.
- Env badge: radius `100px`, padding `8px 14px`, `11.5px/800`, letter-spacing `.05em`.
  App = green tint (`rgba(46,158,91,.14)` / text `#5fd699`); Web = blue tint
  (`rgba(46,120,200,.16)` / text `#7fb4f0`) — **defined but never used**.
- Stage number badge: `54 × 54`, radius `15px`, gradient Signal Gold → `#8f6107`, text `#1c1304`.
- Creative-direction cards: radius `18px`, padding `24px`, gradient `--navy2 → --navy3`.
- Palette swatch: `34 × 34`, radius `9px`.
- Buttons: height `42px`, radius `12px`, `13px/800`. Gold = `linear-gradient(180deg,#E8A020,#C4850A)`
  with text `#1c1304`; ghost = transparent + `1.5px rgba(255,255,255,.22)`; dark = `#16294a`.
- Inputs: height `40px`, radius `10px`, background `rgba(255,255,255,.05)`, 1px hairline, `12px`
  text, placeholder `--t3`.
- Incident tiles (`gtile`): radius `16px`, padding `14px 8px 12px`, translucent white gradient.
- Situation chips (`gchip`): radius `13px`, padding `10px 11px`, gold-tinted border
  `rgba(232,160,32,.4)`.
- Hero shield: `88 × 100`, drop shadow `0 12px 24px rgba(196,133,10,.45)`.
- Overlay/callout scrim: `rgba(7,13,24,.78)`, padding `18px`.
- Sheets: radius `18px`, padding `18px`, background `--navy2`, 1px hairline.
- Disclosure block: `9.5px` text with a `2px` Signal Gold left border.
- Annotation number badge: `24 × 24`, radius `7px`, background `--ink2` `#16294a`, gold text.
- Annotation tag pill: radius `5px`, padding `2px 7px`, `9px/800` caps in Steel Highlight
  `#2E78C8` on `rgba(46,120,200,.12)`.
- Typography scale on the board: masthead H1 `clamp(30px, 4.5vw, 52px)` weight 800, tracking
  `-.035em`; section eyebrows `13px/800` caps tracking `.18em`; card headings `11px/800` caps
  tracking `.14em`; annotation title `13.5px/800`; annotation body `11.5px`, line-height 1.5.

### Motion
- Home guardian shield (screen 27) breathes at rest: a gold aura `.gaura` (170px radial gradient)
  and two rings `.gring.a` (134px) / `.gring.b` (108px, brighter 48% border), all
  `2.4s ease-in-out infinite alternate`. Aura scales `.88→1.1` / opacity `.55→1`; rings scale
  `.94→1.06` / opacity `.5→1`. `.gring.b` carries `animation-delay:-1.2s`, so the inner ring
  breathes half a cycle behind the outer — the two counter-breathe rather than throb in unison.
- Tour spotlight: the focused element is cloned above a blurred, dimmed body inside `.spotring` —
  a `2px` Gold Highlight ring, `inset:-10px`, radius `26px`, animation `spotpulse 1.6s ease-in-out
  infinite`; small-target variant `inset:-5px`, radius `14px`.
- Connecting screen tips rotate every **4000 ms**; suppressed entirely under
  `prefers-reduced-motion: reduce`.
- Welcome screen 4 tool carousel rotates every **3800 ms** with a **760 ms** arrival transition;
  stopped under reduced motion.
- Welcome screen 6 map: 5 activity lights over 26 fixed coordinates, each visible for a random
  **1900–2900 ms**, re-firing after a random **450–1650 ms**; staggered start `220 + n·610 ms`;
  disabled under reduced motion.
- Lottie animations in the welcome carousel autoplay/loop only when reduced motion is off,
  otherwise frozen at frame 0.
- Tour-complete card (21) carries "an animated gold flash pulsing around the card".
- Readiness-card dismissal (`✕`) shifts the situation tiles down and scales the attorney button up;
  the tiles themselves never grow.
- Incident tiles in the connect tray (27A) flash as a button press (`~220 ms`) rather than holding
  a selected state.

### Interaction rules encoded in the reference
- Situation pickers cap selection at **three**; the fourth tap is ignored until one is released.
- Dropzones: tapping an empty dropzone produces an uploaded document tile plus "+ Add another
  document"; deleting the last tile restores the original dropzone.
- Yes/No rows are single-select segmented controls.
- State selectors are custom dropdowns that open an in-frame option list.

---

## Discrepancies and ambiguities in the reference

1. **Only three numbered stages exist.** The masthead claims "5 stages", but the document contains
   headers for Stage 1, Stage 4, and Stage 5 only. There is no "Stage 2" or "Stage 3" header
   anywhere in the page. The plan/checkout/confirmation/return web screens (04–07) — the obvious
   candidates for stages 2 and 3 — sit inside the **Stage 1** section.
2. **The web screens carry a "Native App" badge.** Because 04–07 live inside the Stage 1 section,
   they inherit the "Native App" env badge even though they are browser-chrome frames on
   `attorney-shield.com`. A `.env.web` ("Web") badge style is defined in the stylesheet but is
   never applied to anything.
3. **Screen numbering collides.** The Stage 1 banner says "Screens 1–6 below are the locked
   reference for the app welcome flow", while the annotated screens in the same section are
   numbered 04–07. So "screen 4" is ambiguous: welcome screen 4 ("Built for Your Protection") or
   annotated screen 04 ("Choose plan"). Screens 01–03 are never labelled as such.
4. **"35 screens" understates the board.** There are 66 phone frames: 59 numbered/annotated screens
   plus 7 welcome-carousel frames (an unnumbered intro splash + screens 1–6). The highest plain
   number used is 35, which is likely where "35" comes from, but letter variants (13A–13C, 14A–14D,
   27A/27B, 33A–33D), trial screens (V1, V2, T1–T8), and guest screens (G1–G3) push the real count
   far higher.
5. **"iPhone · 375pt frames" does not match the artwork.** The frames on the board are 292 × 600
   CSS px with a 30px inner radius. The 375pt claim is an intent statement, not the geometry
   present in the file, so all lengths above need rescaling (≈1.284×) if you treat 292 → 375.
6. **The member app has no section header.** Screens 27–35 (plus G1–G3) are rendered inside the
   **B2** row, whose header reads "Branch flow · 7-Day Limited Trial, in-app / When a trial member
   taps to connect". The prose repeatedly refers to a section called "The Member App" (screens 12
   and 14 both say "see The Member App"), but no such heading exists. Likewise the guest flow has
   no header of its own.
7. **Section 6 is numbered 6 but labelled "Stage 5 · in detail"**, so the badge numbers are not a
   clean stage sequence (1, 4, 5, B1, B2, 6, ✦).
8. **"The journey" is an empty section.** It renders as an eyebrow label with a hairline rule and
   no flow diagram content.
9. **Out-of-order screens.** 27B is placed before 27A in the B2 row, and the notification screens
   (22–26) appear after 35 even though they are numbered before 27.
10. **Screen 13B duplicates 27/G2** by design ("identical to the member home (27) … and to the
    guest home (G2)"), so three frames show the same layout; only the status line differs.
11. **Dates are inconsistent across mock data** — footer says June 2026, receipts show
    "Renews Dec 24, 2026", trial ends "Jul 10, 2026", membership started "Jul 3, 2026", grace
    period "until 7/24/26". These are sample values, not a coherent timeline.
12. **Family plan capacity is stated two ways.** 04 says "Covers up to 5 members" / "Includes 3 ·
    add up to 2 more" and 06 shows "You + 3"; T1/T3/T8 say "You + up to 4 members"; 33A says "3 of
    5 on your plan"; 33B says "2 of 4 sub-accounts added. Your FreedomFAMILY plan covers you plus
    up to 4 members." Whether "5" is inclusive of the primary account is genuinely unclear —
    resolve with Attorney Shield before building the stepper.
13. **PIN length**: copy says "A 4-digit PIN with confirm" (note on 12) but the keypad frames show
    no digit count; treat 4 as authoritative from the annotation.

---

## Palette hexes found in this reference

Verbatim from the PALETTE card:

| Name | Hex |
|---|---|
| Protection Navy | `#0D1B2E` |
| Deep Navy | `#0A1626` |
| Signal Gold | `#C4850A` |
| Gold Highlight | `#E8A020` |
| Trust Steel | `#1A5FA8` |
| Live Green | `#2E9E5B` |

Additional hex values used in the reference's own stylesheet/markup but **not** named on the
palette card:

| Hex | Where / role |
|---|---|
| `#112540` | CSS var `--navy2` — card and sheet background |
| `#16294a` | CSS var `--ink2` — dark button fill, annotation number badge |
| `#2E78C8` | CSS var `--steelhi` — steel highlight, annotation tag text |
| `#F5F4F0` | CSS var `--paper` |
| `#070d18` | page background |
| `#1c2740`, `#0b1322` | phone-frame body gradient / notch |
| `#0e1c33` | web-screen background |
| `#1c1304` | text on gold buttons and the stage number badge |
| `#8f6107` | dark end of the stage-badge gold gradient |
| `#5fd699` | "Native App" badge text |
| `#7fb4f0` | "Web" badge text (style defined, never used) |
| `#FFFFFF`, `#F1E0C1`, `#E8A020` | shield logo fills (left/right halves and inner shield) |
| `rgba(255,255,255,.10)` | `--line` hairline |
| `rgba(255,255,255,1 / .66 / .42)` | text tiers `--t1` / `--t2` / `--t3` |
