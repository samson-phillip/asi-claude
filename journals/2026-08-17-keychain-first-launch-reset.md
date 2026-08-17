# 2026-08-17 — Clearing the iOS Keychain on first launch after install

## Task

Close the issue found while verifying the sign-up copy: deleting the iOS app and
reinstalling it left the member signed in.

## Why it happened

Keychain items survive app deletion on iOS. `UserDefaults` does not. Standard
platform behaviour, not a fault in `KeychainSessionStore` — but it is not what
deleting an app is understood to mean, and on a shared or resold device it
leaves a bearer token behind for whoever installs the app next.

## The fix

`FirstLaunchReset` runs **before** `restore()` in `AttorneyShieldApp.init`. It
reads a namespaced flag from `UserDefaults`; an absent flag means this install
has never run, so any session still in the Keychain belongs to a previous one
and is cleared.

Two decisions worth recording:

- **The flag is not tied to a version or build number.** It asks "has this
  install run before", not "has this version run before". An upgrade must not
  sign anyone out. There is a test for exactly that, because it is the obvious
  way to get this wrong.
- **The flag is written before the store is cleared, not after.** If clearing
  fails, a member is signed out once. In the other order, an app killed between
  the two writes would sign them out on *every* launch, forever.

`UserDefaults` is injectable so tests use a throwaway suite rather than the
simulator's real one.

## Android needs nothing

`allowBackup="false"` is already set in the manifest, and Android deletes app
data — including the EncryptedSharedPreferences the session lives in — with the
uninstall. Checked rather than assumed.

## Verification

The unit tests cover the logic. What they cannot cover is the premise, so that
was checked directly on the simulator:

| Step | Result |
|---|---|
| First launch of a fresh install | flag written: `hasLaunchedSinceInstall => true` |
| After `simctl uninstall` | defaults container **gone** |
| After `simctl uninstall` | keychain still holds **64 rows** |
| Reinstall, before launch | flag **absent** → reset will fire |
| Reinstall, after launch | flag written again → reset ran |

That is the asymmetry the fix depends on, demonstrated rather than assumed. The
app now opens on the welcome carousel after a reinstall instead of Home.

A full end-to-end pass (sign in → delete → reinstall → confirm signed out) still
needs a real OTP code, so it was not run. The four unit tests cover the clearing
itself, including that a session left by a previous install does not survive.

## Tests

| Suite | Result |
|---|---|
| iOS unit | **421 / 421**, 0 failed (+4 new) |

One snag: the first version of the tests used a `MemberContext` initialiser that
does not exist — `email` and `jurisdictionId` are required. The build had
"succeeded" beforehand because the app target compiles independently of the test
target, which is a good reminder that `xcodebuild build` passing says nothing
about the tests compiling.

## Files

- `swift`: `Core/Session/FirstLaunchReset.swift` (new), `AttorneyShieldApp.swift`,
  `AttorneyShieldTests/FirstLaunchResetTests.swift` (new).
