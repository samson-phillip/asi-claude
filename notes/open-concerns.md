# Open concerns — for discussion

Things I decided on my own that you may want to revisit, and risks I can't
resolve from inside the code. Separate from
[backend-gaps.md](backend-gaps.md), which tracks what we need *from other
people*.

Last updated: 2026-08-13, after building the Glovebox.

---

## 1. App Store / Play compliance is the biggest unmanaged risk

The product sells a digital subscription through **web Stripe** and deep-links
back. Apple's rules on purchases of digital content and on steering users to
external payment are the single most likely cause of a rejection, and a rejection
here invalidates the flow rather than delaying it.

The design reference already shows someone has thought about part of this —
screen 33A carries Apple's required delete-account wording, and there are
deliberately no in-app plan changes. So somebody may already know the intended
answer.

**I'd want this settled before Phase 3 is scoped, not at submission.** It is the
one open item that could force a redesign rather than more work.

## 2. `com.app.attorney.shield` is already live at versionCode 126

An emulator here had it installed — internally `com.example.attorneyshield`. So
ASI 2.0 replaces a shipping app rather than launching fresh.

Consequences:
- Debug builds now carry a `.debug` suffix so we never clobber anyone's install.
- **The first 2.0 release build needs a `versionCode` above 126.** Worth
  confirming the real store versionCode before we cut one.
- An in-place replacement means existing members will update into an app with a
  different data model and no migration path. Nobody has mentioned migration.

## 3. A real video call has never connected

`member-call` returns `409 no attorney is available` on dev, so the step from
"connecting" to a live picture is the one part of the product still taken on
faith. Proven: the SDK loads, reaches Vonage, and reports through our phase
machine. Not proven: a valid session going live, subscriber video rendering, or
mute actually silencing the stream.

This needs a window with a dev attorney online. It is the last thing I'd want
unverified before a release.

## 4. Scope: the app is much smaller than the design

The reference is 66 frames. We have built the spine — welcome, login, home,
call, deep link — because that is what the API supports. Roughly two thirds of
the design has **no backend at all** (registration 08–12, document vault, family
sub-accounts, activity, nudges, trial and guest flows).

If the expectation is "the app matches the CodePen", that expectation is
currently unmeetable and the gap is backend, not frontend. Worth making sure
whoever set the deadline knows that.

## 5. Decisions I made that are reversible but worth a look

- **Android is now locked to portrait**, matching iOS and the reference. This is a
  deliberate accessibility trade-off: someone who mounts their phone in landscape
  cannot. It also removes rotation as a way to destroy a call mid-encounter, which
  is why I chose it — but it is a product call, not a technical one.
- **Home omits the reference's saved-three-situations row and the
  Glovebox/Activity/Profile tab bar.** No endpoints for the former; the tab bar
  points at screens that do not exist yet. I judged navigation to nowhere worse
  than leaving it out. The readiness card **is** now built.
- **Sign-in codes are 4 digits, not the 6 the design shows.** The design
  reference's six-cell entry (screen 09) is registration *phone* verification;
  the live sign-in code is 4 digits and the deployed web client submits on the
  fourth. I followed the live system. One constant to change if that is wrong.
- **Being signed out elsewhere gives no explanation.** Only one device may be
  signed in at a time, so signing in on the web kills the app's session — the
  member just gets "Your session has expired". The reference says "Your account
  was opened on another device", and `mySessionStatus { status reason }` returns
  `another_device`, so the information is available. Contained follow-up, but a
  bad moment to be confused.
- **SMS delivery is built but never exercised.** No dev account has a verified
  phone, so `maskedPhone` is always null and the channel switch never renders.
- **The finish-setup wizard is skippable at every step, which the design is not.**
  "Finish later" goes straight to Home. My reasoning: this app gets opened during
  a police encounter, and a required form standing between a member and an
  attorney is a worse failure than an incomplete profile. It is a product call
  and you may want it required instead.
- **A state picker was added to the address screen**, which the CodePen does not
  show. The profile carries `subdivisionId`, the screen's own info chip promises
  "your home jurisdiction", and a US address with no state is incomplete. Shown
  only when the list resolves.
- **No age gate.** Date of birth is validated as a real past date, but nothing
  checks 18+. If membership has a minimum age, someone needs to say so.
- **Setup completeness is inferred** from DOB + address + PIN + password +
  contacts, because there is no "onboarding complete" flag. If one appears we
  should use it instead. It drives both the checklist and Home's percentage, from
  one shared loader so the two cannot disagree.
- **The readiness card's dismissal is not persisted** — it hides for the session
  only, so an incomplete profile is raised again next launch. The reference shows
  a cross; it does not say whether it should stick.
- **Errors and hang-up are rendered in gold, not red.** The palette forbids the
  red it names and supplies no error colour. This is a real visual compromise on
  the most safety-critical control in the app, and it needs a Blue Sky decision.
- **No client-side email validation.** Deliberate: the server decides whether an
  address exists, and a regex that rejects a valid address locks someone out of
  their own account.
- **Deep-link URL paths are guessed** (`/app/return`, `/return-to-app`, `/app`),
  confined to one file.
- **Android `namespace` stays `com.attorneyshield.member`** while the
  applicationId is `com.app.attorney.shield`. Valid and independent, but if you
  want them to match, say so before the codebase grows.
- **Inter is not bundled** — licensing unconfirmed, so both platforms use the
  system face mapped to the brand weights.

## 6. Things owed that are on me, not blocked

- A **visual pass over Home and Call**. Both are verified on-device by assertion,
  not by eye, because reaching Home needs a login. The clipped-tile bug earlier
  proved text assertions miss layout faults.
- **No launcher icon or brand shield asset.** The lockup draws a placeholder
  shield in gold.
- **The iOS file pick is unverified on a device.** The importer presents, but a
  clean simulator has nothing to pick and seeding a document is not
  representative. Reading bytes from a security-scoped URL is covered by unit
  tests and by parity with Android, not by a real pick. One manual pick on a real
  iPhone would close it.
- **No camera capture.** The design's document screens show [Camera] [Gallery];
  we ship a document picker, which covers photos and PDFs but not capture.
- **No in-app document viewer.** "Open" hands the presigned URL to the browser.
  A real viewer is a bigger job, and faking a preview would be worse.
- **`iconFilePath` now carries real CloudFront URLs and we still draw emoji.**
  Before seeding this was theoretical; now it is a visible gap against the design
  on the app's main screen. Android needs an image-loading dependency (Coil); iOS
  has `AsyncImage` built in. Mine to do.
- **The dev machine is at 6.7 GiB free** and the emulator died twice during the
  readiness-card work, costing two test runs. Worse than when I last raised it.
- Android's system nav bar renders light under `enableEdgeToEdge()`, ignoring the
  theme. Cosmetic.
- **Release signing uses the debug key.** Temporary, so a minified build could be
  smoke-tested at all. **A real keystore is needed before shipping**, and whoever
  holds it should also confirm `versionCode` against the live store listing — I
  set 127 from a dev device showing 126, which is a guess.
- **Serialization and the Vonage call path are unverified under R8.** The minified
  build launches and navigates cleanly, but reaching the decode and call paths
  needs a login the gateway URL still blocks.

## 7. The dev machine

**Disk is down to 6.7 GiB free**, from 13 GiB when I first raised this. The
Android emulator has now died mid-run on three separate tasks, and each death
costs a full test cycle. I cleared 9.6 GiB earlier by removing DerivedData and
build output; that has been re-consumed. The remaining large items I deliberately
did not touch are iOS DeviceSupport (~12G) and `~/.gradle/caches` (~13G) — both
are safe to delete but slow to rebuild, so that is your call.

## 8. Two process notes

- **`gh`'s active account silently drifted to `samson-mm` mid-session** and a push
  failed. Worth knowing it can flip while you work; the startup checklist catches
  it.
- **The CodePen contradicts itself in 13 documented places** (see
  `design-reference-codepen.md`), most importantly that the family plan capacity
  is stated four different ways. That one blocks building the member stepper and
  needs Attorney Shield to rule.
