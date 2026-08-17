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
