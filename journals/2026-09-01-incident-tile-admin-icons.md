# 2026-09-01 — Honour admin icons on incident tiles (member-client parity)

## Context

Parity pass after pulling member-client (HEAD #147). Its commit `90e1b5b`
("Draw the icon the admin actually picked, on tiles as well as documents") and
`b24f599` ("per-type icons") extend admin-icon rendering to the **Home incident
tiles** — it draws `t.iconFilePath` through the same `IconValue` (URL / Lucide
name / emoji) it uses for documents.

Our #5 work honoured the admin icon on **Glovebox document sections** only. The
incident tiles still ignored `IncidentType.iconFilePath` (which we already fetch:
`adminIncidentTypeList { id code iconFilePath sortOrder }`) and drew the
code-keyed glyph, with a comment noting "no image loader is wired yet."

## Change (both platforms)

Reused the #5 resolver. Extracted the shared resolution (`URL → Remote`,
`Lucide/Feather name → glyph`, else the bundled fallback) into a private helper
and added **`AsiIcons.incidentIcon(code, iconFilePath)`** alongside
`sectionIcon` — identical rules, but the fallback is the **incident** code glyph
(`incident(code)`), not a section glyph.

The Home `IncidentTile` now draws the resolved icon:

- **iOS** — a URL renders via `AsyncImage` (with the code glyph as fallback while
  loading / on failure); a Lucide name → an SF Symbol; else the code glyph. The
  locked/unlocked tint still applies to the symbol/asset cases.
- **Android** — a Lucide name → the nearest bundled glyph; a URL falls back to
  the code glyph until an image loader (Coil) is wired (same asymmetry as the
  Glovebox sections, documented there); else the code glyph.

## Files

- Swift: `Core/Design/AsiIcons.swift` (shared `resolveIcon` + `incidentIcon`),
  `Feature/Home/HomeScreen.swift` (`IncidentTile.tileGlyph`); test
  `AsiIconsTests.swift`.
- Kotlin: `core/design/AsiIcons.kt` (shared `resolveIcon` + `incidentIcon`),
  `feature/home/HomeScreen.kt` (`IncidentTile`); test `AsiIconsTest.kt`.

## Tests

New on both platforms: an incident Lucide name resolves to a glyph; a URL is
`Remote` carrying the **incident** code fallback; an absent/blank icon falls back
to the incident code glyph.

- Swift: `AsiIconsTests` (single-process, iPhone 16 Pro) → **13 tests passed**,
  `** TEST SUCCEEDED **`.
- Kotlin: `AsiIconsTest` → **BUILD SUCCESSFUL**.

## Not done in this pass — the in-app document reader (bigger, needs go/no-go)

member-client's `b24f599` also added an **in-app DocumentViewer** (image
pinch/rotate, PDF pages via pdf.js), replacing `window.open(presignedUrl)` — it
explicitly calls the old behaviour "a one-way trip out of the Glove Box." Our
apps still do exactly that old thing: fetch `userDocumentDownloadUrl` and hand it
to the OS (`UIApplication.shared.open` → Safari on iOS; an external open on
Android). That's a real UX gap but a **feature-sized** one; the dependency-free
route is **QuickLook** on iOS + **PdfRenderer** (+ image decode) on Android.
Flagged for a separate go/no-go rather than bundled here.
