# 2026-09-09 — Profile photo upload (both apps) + member-client #159 noted

Samson: "allow a user to update their profile photo," plus the daily member-client
parity check.

## member-client update

One new commit since 8a17bf0: **#159 f6b01fd "David V3"** — two unrelated things,
neither profile-photo:
1. **Enrollment run** now gated on a *derived* "enrollment ladder" (verified
   mobile + address + **Sex, now required** + DOB + PIN) rather than the
   `onboarding_completed_at` flag; a returning canceled/expired member holding all
   four gets a single "Step 1 of 1" (new PIN). Unknown fails closed.
2. **Sub-account counts** — Plan Details now "Subaccounts · 2 of 3 used" (was
   miscounting the primary + unpurchased seats; badge gone); Sub Accounts screen
   shows each person's email, "Included" stops counting the primary, empty
   purchased seats are flagged.

Both are **native parity candidates** (registration gating + required Sex;
family/seat counting + display) — logged for a **separate** parity pass, not folded
into the photo work. Not yet done on kotlin/swift.

## Profile photo — shipped on both apps

The member-client contract (`src/lib/profileApi.ts` `uploadAvatar`) is a 3-step
presigned upload, identical in shape to the Glovebox document upload both native
apps already have:
- `requestUserProfileImageUpload(fileName, contentType, sizeBytes) { uploadUrl method headers { name value } key }`
- HTTP **PUT** the bytes to `uploadUrl` (no bearer — the presigned URL is the credential)
- `finalizeUserProfileImageUpload(key) { profileImageURL }`
- read-back: `userProfileByUser { … profileImageURL }`

Implementation reused each app's existing `uploadDocumentBytes` for step 2 (a
presigned PUT is a presigned PUT). The avatar edit lives on the **Edit Profile**
pane (where both apps had left a deliberate ghost avatar "rather than shipped
dead"); the photo also renders on the account hub. A gold camera badge marks the
affordance and spins while uploading.

- **Android** (`kotlin → dev 5a03f73`): `PickVisualMedia` picker; content Uri
  decoded to bytes off the main thread; **Coil** added (`coil-compose 2.7.0`) for
  remote avatar display (`AsyncImage`). New: `AsiApi.requestProfileImageUpload` /
  `finalizeProfileImageUpload`, `AccountViewModel.uploadAvatar`, `EditableAvatar`
  composable, `ic_camera` drawable. Verified `:app:testDebugUnitTest` green + 5 new
  `AsiApiTest` cases.
- **iOS** (`swift → dev 594a6ff`): `PhotosPicker` + SwiftUI `AsyncImage` (no new
  dependency); `PhotosPickerItem` → `Data` + UTType-derived contentType/filename.
  New: same two `AsiApi` methods, `AccountViewModel.uploadAvatar`, `AvatarEditor`
  view. Verified `xcodebuild test` (AsiApiTests) **TEST SUCCEEDED** + 5 new cases;
  full app + UI compiles.

No backend change — the mutations already exist (member-client uses them).

## Note

member-client's avatar is delivered by the SAME gateway both native apps use, so
unlike the Maps key there's no environment/key question here — `profileImageURL`
comes straight off `userProfileByUser`.
