# 2026-08-17 — Home screen rebuilt to the design

## Task

Assess the Home screen against the CodePen reference and update both apps to
match the client mockup.

## Reference

Markup at `code_pen_design.html` ~9108–9215; CSS for `.iconbtn`, `.greet2`,
`.gname`, `.gcover`, `.ghero`, `.gstage`, `.gaura`, `.gring`, `.gshield`,
`.gtitle`, `.gsub`, `.gqlbl`, `.chgl`, `.gchip`, `.gready`, `.grring`, `.bnav`.

## What changed

| Element | Reference | Was | Now |
|---|---|---|---|
| Hero | Shield lit on the navy: 170px gold bloom, rings at 134/108px, 88×100 mark | Gold filled card with a 🛡 emoji | Rebuilt to the reference |
| Brand | Gold badge + wordmark in caps | Bare mark + title case | Badge + caps |
| Bell / account | Two 34px rounded squares, line icons | Emoji bell in a circle; initialled circle | Matching square pair |
| Coverage | Green-tinted pill with a ring dot | Bare dot + muted text | Pill |
| Readiness | Green-tinted card, 34px completion ring | Surface card, eyebrow + linear bar | Ring on a green tint |

## Three faults this turned up

- **The shield mark was wrong.** `brand_shield.png` is the squat wordmark badge;
  stretched to 88×100 it read as a tent. Replaced with the reference's own
  heraldic shield, transcribed path for path — `ic_brand_shield.xml` on Android,
  an SVG in the asset catalog on iOS.
- **`Color.Transparent` left a dark halo.** The aura ramped gold → Transparent,
  which is transparent *black*, so it darkened as it faded. It fades to
  transparent gold instead. Worth remembering for every gradient we write.
- **An XML comment containing `--` broke the resource build.** Illegal inside an
  XML comment; the failure surfaced only as a `parseDebugLocalResources` error,
  and a stale APK installed happily in the meantime.

## Colour rulings

- The reference's row/link blue `#2E78C8` and its light green `#5fd699` are both
  outside the palette. Links take the accent; the coverage label stays white and
  the green lives in the tint, border and dot (R4 — Verified Green is 3.24:1 on
  navy, a fill colour and never text).
- The hero mark carries its own colours, the same precedent as
  `brand_shield.png`. Two cream tints (`#F1E0C1`, `#F6E8CC`) exist only inside
  the asset, never in code — which is also why iOS got an SVG rather than
  SwiftUI paths: the palette guard scans every `.swift` file.

## Verification

Android was not signed in, so Home was rendered from a throwaway instrumented
test holding it on screen while the device was screencapped. That took three
attempts worth recording: the first sampled after the hold had expired, the
second used a "non-background pixels" heuristic that matched the launcher
wallpaper, and only a detector requiring *both* the app's navy at two known
points and a content count found the real frame. The test was deleted after.

iOS was checked live on the signed-in simulator session.

| Suite | Result |
|---|---|
| Android unit | **432 / 432**, 0 failed |
| Android instrumented | **30 / 30**, 0 failed |
| iOS unit | **413 / 413**, 0 failed |

`ScreenRenderTest` needed one assertion updated: the coverage label now uses the
reference's middle dot rather than a hyphen.

## Left deliberately different

- **The mockup shows three dashed "Add situation" slots where we show the full
  incident list.** That is the documented fallback: an empty saved-situations
  read is indistinguishable from a failed one, and the backend's instruction is
  to fall back to everything. Matching the mockup here would remove a member's
  one-tap path to an attorney, so it is a product call, not a styling one.
- **The tab bar still uses emoji** where the reference has line icons.
- **Incident tiles still use emoji**, pending the `iconFilePath` work already
  recorded in open-concerns.
- `Open your Glovebox` and the routing hint are ours, not the design's. The
  button duplicates the tab bar exactly and is a candidate for removal.

## Next

Guest sign-up confirmation is still outstanding — see the 2026-08-16 addendum.
`guest_user` has never been observed coming back from the live gateway.

---

## Addendum — tab bar and incident tile icons

Ten glyphs transcribed from the reference, replacing emoji throughout:

| Where | Icons |
|---|---|
| Tab bar (`.bn`) | home, glovebox, activity, profile |
| Incident types | traffic signal, walking figure, car, two figures, handset, plus-in-square |

Emoji were the wrong tool: they render differently on every OS version, carry
their own colour so they cannot take the accent, and read as decoration rather
than as part of the brand.

### Where the map lives now

`IncidentIcons` sat in `core/network/AsiConfig` and returned an emoji string.
It now resolves a **drawable**, so it moved to `core/design/AsiIcons` — the
network layer has no business knowing about resources. Its three tests moved
with it and gained a fourth: that the fallback is not silently identical to a
real tile's icon, which the old emoji map could not have caught because the
generic shield and no other tile shared a value.

Android gets VectorDrawables; iOS gets SVGs in the asset catalog with template
rendering, so both tint from the palette. Same reasoning as the hero shield —
nothing lands in a `.swift` file for the palette guard to trip over.

### Three faults found by looking

- **The bell's unread badge was being shaved off.** It sits proud of the corner,
  and the container carried the rounded-square clip, so the clip cut it. The
  clip now belongs to an inner box. Only visible once a badge was actually
  rendered — the earlier Home capture had `unreadCount = 0`.
- **Two of the four tab paths were wrong on first transcription.** The profile
  circle was centred at `cy=4` instead of `cy=8`, and the glovebox rect started
  at the corner rather than after the radius, which a rounded rect cannot do.
  Both were caught by rendering, not by review.
- **Three orphaned drawables** (`ic_incident_car`, `ic_incident_pedestrian`,
  `ic_incident_questioned`) survive from commit 4927f7e as 48dp screen-2 icons
  with no references anywhere. Flagged for separate cleanup rather than folded
  in here; they are *not* the same glyphs as the new 24dp set.

### Tests

| Suite | Result |
|---|---|
| Android unit | **433 / 433**, 0 failed (+1 net: 3 emoji tests → 4 icon tests) |
| Android instrumented | **30 / 30**, 0 failed |
| iOS unit | **417 / 417**, 0 failed (+4 new) |

Android verified by the held-instrumented-test capture again; iOS verified live
on the signed-in simulator. Both platforms render identically.

### Still open on Home

- The mockup's three dashed "Add situation" slots vs our full-list fallback —
  unchanged, and still a product call.
- `Open your Glovebox` and the routing hint are ours, not the design's.
- Uploaded `iconFilePath` icons are still unrendered; every tile falls back to
  the bundled set.
