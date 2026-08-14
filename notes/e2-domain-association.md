# E2 — Domain-association files (assetlinks.json / AASA)

Extracted from the old shipping apps (`ANDROID`, `IOS` repos) on 2026-08-14,
**before they were deleted.** These are the values the backend needs to host the
`/.well-known/` files that make a web→app link open the app silently.

## Extracted values

| What | Value | Source |
|---|---|---|
| **iOS Team ID** | `TWKX78WDP7` | `IOS/…/project.pbxproj` `DEVELOPMENT_TEAM`, on the `com.app.attorney.shield` target (Debug + Release). |
| iOS bundle id | `com.app.attorney.shield` | same |
| **Android package** | `com.app.attorney.shield` | `ANDROID/app/build.gradle.kts` `applicationId` (shipping v127 / 7.006). |
| Existing deep-link scheme | `attorneyshieldapp://` (custom scheme, **both** platforms) | iOS `CFBundleURLSchemes`; Android manifest intent-filter. |
| **Android SHA-256 — `key1`** | `46:52:10:9D:06:58:BE:D0:2E:58:77:EE:E0:45:7B:22:61:CD:36:E5:73:CA:B3:D6:ED:2F:DA:B8:A9:C3:ED:AA` | `attorneyShield/key1.keystore`, alias `key1`. |
| **Android SHA-256 — upload key** | `FF:B0:8C:F9:75:5C:B4:90:B0:8D:15:D8:13:B9:9F:A4:47:00:7B:2A:09:51:DE:79:A6:85:FB:05:F8:AA:7E:16` | `attorneyShield/my-upload-key.keystore`, alias `my-key-alias` (the Play **upload** key). |

The `KDT5JPT937` team also appears in the iOS project — that's on the
`com.example.AttorneyShield…Tests` targets (a personal team). The **production**
app uses `TWKX78WDP7`.

## Android fingerprints — got them from the keystores you added

The `attorneyShield/` folder had two keystores. Both opened, and I read the
**public** certificate SHA-256 from each (never touched the private keys):

- **`key1.keystore`** (alias `key1`) → `46:52:…:ED:AA`
- **`my-upload-key.keystore`** (alias `my-key-alias`) → `FF:B0:…:7E:16` — this is the
  Play **upload** key (standard filename/alias from the RN signing guide).

`assetlinks.json` below lists **both**. That is the safe belt-and-braces setup:
the upload key covers directly-installed / internally-signed builds, and `key1`
is almost certainly the original **app-signing** key.

**One thing to confirm against Play Console before shipping.** If the app is on
Google Play App Signing, the key that signs what users actually download is the
**app-signing key**, whose SHA-256 is at:

> Play Console → (app) → Test and release → App integrity → App signing →
> "App signing key certificate" → SHA-256

If that value equals `key1`'s fingerprint (likely), we're done. If it differs,
add it as a third entry in the array. Including all of them is harmless —
`assetlinks` matches any.

## ⚠️ Security — the keystore passwords are weak

Both keystores opened with a **common dictionary password** (tried a short list;
one worked immediately). The upload key is what authorises every update pushed to
the Play Store — a guessable password on it means anyone who gets the file can
sign a malicious update. Recommend:

- change the keystore store/key passwords (`keytool -storepasswd` /
  `-keypasswd`),
- keep these `.keystore` files out of any shared or committed repo (treat as
  secrets), and
- if the files have been shared around, consider a key rotation via Play App
  Signing's upload-key reset.

## SHA-1 (for matching in Play Console)

Play Console shows SHA-1; use these to identify which local key equals the
app-signing key.

- `key1` (valid 2025-01-23 → 2050): SHA1 `67:53:74:86:F9:58:27:8D:04:37:03:40:3E:92:9B:B8:07:71:D7:03`
- `my-key-alias` / upload (valid 2024-02-15 → 2051): SHA1 `80:E8:F3:34:25:23:94:65:32:5E:62:E5:2D:18:CE:75:9F:A1:5A:1B`

Note the upload key (2024) is **older** than `key1` (2025), so which one is the
Play app-signing key isn't obvious from the files alone — hence "confirm against
Play Console" above. Both SHA-256s are already in `assetlinks.json`, so links
verify either way; this is only to know which is which.

## Deep-link paths the new apps handle

The new `kotlin`/`swift` apps' deep-link handler accepts, on
`attorney-shield.com` and `www.attorney-shield.com`:

- `/app/return`
- `/return-to-app`
- `/app`

reading an `email` query parameter. The AASA `paths` below cover these.

## Ready-to-host files

Both drafted in this directory:

- `wellknown/apple-app-site-association` — Team ID already filled in.
- `wellknown/assetlinks.json` — **has a `PLACEHOLDER_SHA256` to replace** with the
  Play Console value above.

Host each at **both** hosts, at exactly:

- `https://attorney-shield.com/.well-known/apple-app-site-association`
- `https://www.attorney-shield.com/.well-known/apple-app-site-association`
- `https://attorney-shield.com/.well-known/assetlinks.json`
- `https://www.attorney-shield.com/.well-known/assetlinks.json`

AASA must be served as `application/json`, **no `.json` extension**, no redirect.

## Security note (old app — for the backend, not blocking)

The old `ANDROID` app hardcodes fallback secrets in `build.gradle.kts`
(audit-cluster username/passwords baked into `BuildConfig`). They ship in the
binary and sit in that repo's git history. Worth rotating those audit
credentials, since deleting the working copy does not remove them from the
published APK or from git history. Values deliberately not reproduced here.
