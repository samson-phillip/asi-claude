# 2026-09-01 — Android: subsequent calls never connected (root cause + fix)

## Symptom

First call connected fine; every call after it jumped straight to "Call ended"
and **only an app restart** restored the ability to call. An earlier nonce fix
(2cb0801) did not help.

## Root cause (found via on-device logcat)

The call screen's `CallViewModel` is created with `viewModel(key = …)`, and a
`viewModel()` for a given key returns the **retained** instance. The key was
written:

```
key = "call-${'$'}{call.nonce}"
```

In Kotlin `${'$'}` inserts a **literal `$`**, so that string is the *compile-time
constant* `"call-${call.nonce}"` — `call.nonce` was never interpolated. So the key
was identical for every call, `viewModel()` handed back the **same** view model
for the whole app session, and the second call inherited the first call's `Ended`
phase + credentials. The ViewModelStore only clears on process death → "works
again after a restart."

This same `${'$'}` was in the **original** key (`call-${'$'}{type.id}-…`), so the
call VM had always been a de-facto singleton; the nonce fix didn't help because it
carried the identical escaping.

The logcat made it unmistakable: on the second call there was **no `start()`
invoked**, and the `DisposableEffect` fired with `credentials=true phase=Ended`
(the first call's state) — proof the VM was reused.

> Note: the other 116 `${'$'}` in the codebase are all in `AsiApi.kt` GraphQL
> query strings, where a literal `$` is **correct** (GraphQL variable syntax,
> `$input`). Only the view-model key was wrong. Left those untouched.

## Fix (`kotlin`, `MainActivity.kt`, one line)

```
key = "call-${call.nonce}"      // real template; unique per call attempt
```

Combined with the existing nonce (bumped in `begin()`, carried on `PendingCall`),
every call attempt now gets a genuinely fresh `CallViewModel` whose
`init { start() }` places a new call.

## Verified on device (emulator, fresh logcat)

Four consecutive calls in one app session, each with its **own** `start()`, its
**own** unique `callId`, connecting → live → ended:

```
nonce=1 callId=cb565914 … subscriber connected -- live … end
nonce=2 callId=bc6c59cc … subscriber connected -- live … end
nonce=3 callId=b1363923 … subscriber connected -- live … end
nonce=4 callId=edb6ec95 … connected
```

User confirmed: "second and third calls connect now."

`compileDebugKotlin` + `feature.call.*` unit tests green. iOS unaffected (it builds
a new `CallViewModel` per call directly).

## PIN note (not a regression)

Every call ended via `end()` directly — `pinRequired` was false — i.e. the test
account has **no PIN set**, so no prompt is correct. The PIN logic is unchanged;
with the fix, a fresh VM re-runs the `isPinSet` lookup per call, so an account
that *does* have a PIN will be gated. To confirm with the user.

## Files

- `kotlin/app/src/main/java/com/attorneyshield/member/MainActivity.kt`
