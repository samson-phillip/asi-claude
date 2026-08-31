# Scope — in-app document reader (Glovebox)

**Status:** scoping only, awaiting go/no-go on the Android approach.
**Parity driver:** member-client `b24f599` added an in-app `DocumentViewer`,
replacing `window.open(presignedUrl)` — it calls the old behaviour *"a one-way
trip out of the Glove Box."* Both our apps still do that old thing.

## Goal

Tapping **View** on a stored document opens it **over** the Glovebox and closes
back onto it — never kicking the member out to a raw S3 URL in a browser. Handle
the two kinds a member actually stores: **images** (their licence, photographed
sideways) and **PDFs** (insurance cards, policies).

## Current state (what we replace)

Both platforms fetch the presigned URL and hand it to the OS browser:

- **iOS** — `GloveboxScreen` `onOpen` → `model.downloadUrl(for:)` →
  `onOpenUrl` → `UIApplication.shared.open(url)` (Safari). Comment already admits
  *"no viewer is built."*
- **Android** — `onOpenDocument` → `glovebox.openDocument(id)` →
  `startActivity(Intent(ACTION_VIEW, Uri.parse(url)))` (external app / browser).

The download query already exists on both: `userDocumentDownloadUrl(id)`
(`AsiApi.documentDownloadUrl`). `SavedDocument` already carries `fileName` +
`contentType` — enough to pick the renderer.

## Reference behaviour (member-client)

- `getDocumentDownloadUrl(id)` → same `userDocumentDownloadUrl` query.
- `documentKind({name, type})` → `image | pdf | unknown`: PDF by mime/extension,
  else `image/*` mime or an allowed image extension, else unknown.
- `displayDocumentName(fileName)` → a human title (strips the key path, describes
  the type when the stem looks like a generated id).
- Renderer chosen by kind: **image** = one surface to pinch / drag / rotate;
  **PDF** = scrollable pages (lazy-loads pdf.js, ~400 KB, only when a PDF opens).
- Dismiss three ways: **X**, **Escape**, **swipe-down** (shared sheet-gesture
  thresholds). Opens instantly and spins while the presigned URL resolves.

## Proposed design — native, dependency-free on both

### Shared (pure, testable, mirrors the reference)

- `DocumentKind` (`image | pdf | unknown`) from `contentType` + `fileName`
  extension — a direct port of member-client's `documentKind`.
- `displayDocumentName(fileName)` — port of the reference's title logic.
- A small **download-to-temp** step: QuickLook and `PdfRenderer` both need a
  **local file** (or fd), not a URL. New helper: fetch the presigned URL bytes →
  a temp file → hand its local URL to the viewer. (The presigned URL is
  short-lived, so download on open, don't cache the URL.)

### iOS — QuickLook (`QLPreviewController`)

- Wrap `QLPreviewController` in a `UIViewControllerRepresentable` (or the
  `.quickLookPreview($url)` modifier) presented as a full-screen cover over the
  Glovebox.
- Flow: fetch URL → download to temp `.pdf`/`.jpg` (extension from kind) →
  present. QuickLook gives image **and** PDF, pinch-zoom, rotate, page scroll,
  and Share for free, and dismisses back to the Glovebox natively.
- Loading spinner + an error state ("Couldn't open this document. Try again").
- **Effort: small (~0.5 day).**

### Android — two options (THE decision)

`PdfRenderer` + `BitmapFactory` are built in (API 21+); **no new dependency**.

- **Option A — full in-app viewer (faithful).** A Compose overlay: for a PDF,
  `PdfRenderer` renders pages to bitmaps in a zoomable `LazyColumn`; for an
  image, decode to a bitmap in a pinch-zoom `Box`. Dismiss via back / swipe-down.
  Matches member-client and iOS. **Effort: ~1–1.5 days** (page rendering +
  pinch-zoom are the bulk).
- **Option B — `FileProvider` + `ACTION_VIEW` (pragmatic).** Download to a temp
  file, share it via `FileProvider`, `ACTION_VIEW` to the user's PDF/photo app.
  Still leaves our app, but to a real viewer with a proper Back — not a raw S3
  URL in a browser. **Effort: ~0.25 day.** Less faithful; iOS would be in-app
  while Android hands off, an asymmetry.

**Recommendation:** iOS QuickLook + Android **Option A** for true parity —
dependency-free on both, both in-app. If speed matters more than parity, ship
Android Option B first and upgrade to A later; the `documentKind` +
download-to-temp plumbing is shared either way, so B → A is not throwaway.

`unknown` kind (a stored file we can't classify): keep the current external open
as the fallback on both platforms, with a one-line "opening externally" note.

## Files touched

- Swift: new `Feature/Glovebox/DocumentViewer.swift` (QuickLook host + state);
  `Core/Format/DocumentKind.swift` (kind + display name);
  `Core/Network/AsiApi.swift` (download-bytes-to-temp helper);
  `Feature/Glovebox/GloveboxViewModel.swift` (present/dismiss + fetch) and
  `GloveboxScreen.swift` / `AttorneyShieldApp.swift` (swap `onOpenUrl` for the
  viewer). Tests: `DocumentKindTests`, viewer-state tests.
- Kotlin: new `feature/glovebox/DocumentViewer.kt` (Option A overlay) or a
  `FileProvider` route (Option B); `core/format/DocumentKind.kt`; download helper
  in `AsiApi.kt`; `GloveboxViewModel.kt` + `GloveboxScreen.kt` + `MainActivity.kt`
  wiring. `FileProvider` in the manifest if Option B (or for sharing). Tests:
  `DocumentKindTest`, viewer-state tests.

## Tests

- `documentKind` / `displayDocumentName` — pure, both platforms, ported cases
  from `member-client/src/lib/uploads` (mime, extension, no-mime HEIC, generated
  key → described type).
- Download-to-temp: stubbed URL → a temp file with the right extension; a failed
  download → error state, no crash.
- Viewer state machine: loading → loaded → dismiss; error path; `unknown` →
  external fallback.

## Edge cases / risks

- **Presigned URL expiry** — download on open; never cache the URL.
- **HEIC images** — QuickLook decodes them on iOS; Android `BitmapFactory` may
  not on older APIs (Option B / QuickLook-style app handoff sidesteps this).
- **Temp-file cleanup** — write under the cache dir; delete on dismiss.
- **Large PDFs** — native `PdfRenderer` streams pages, so no web-style bundle
  concern; still render pages lazily.
- **Auth on the download** — the presigned URL is the credential; do NOT attach a
  bearer token to the S3 GET (same rule the upload path already follows).

## Effort summary

- Shared (kind + name + download helper + tests): ~0.5 day.
- iOS QuickLook: ~0.5 day.
- Android Option A: ~1–1.5 days · Option B: ~0.25 day.
- **Total: ~1.25 day (B) to ~2.5 days (A), both platforms, with tests.**

## Open decisions (need answers before building)

1. **Android: Option A (full in-app viewer) or Option B (FileProvider handoff)?**
   Recommend A for parity; B if we want it fast and iterate.
2. Ship image + PDF together, or **PDF-first** (the case that most needs an
   in-app reader — an image already previews acceptably even externally)?
3. Keep the **external open** as the `unknown`-kind fallback? (Recommend yes.)
