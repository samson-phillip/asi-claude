# 2026-09-01 — In-app document reader (Glovebox) — Option A, both platforms

## Task

Parity with member-client's `DocumentViewer` (`b24f599`): view a stored document
**over** the Glovebox and close back onto it, instead of `window.open`-ing the
presigned URL. Both our apps did the mobile equivalent — fetch
`userDocumentDownloadUrl` and hand it to the OS browser
(`UIApplication.shared.open` / `ACTION_VIEW`), a one-way trip out to a raw S3 tab
to look at your own licence. User chose **Option A** (full in-app viewer on both,
dependency-free); defaults for the other two decisions: **both image + PDF**, and
**external open as the `unknown`-kind fallback**.

## Shared, pure, tested (ported from member-client `uploads.ts`)

`DocumentFile` on both platforms:

- `kind(fileName, contentType) → image | pdf | unknown` — PDF by mime/extension,
  else `image/*` mime or an allowed image extension, else unknown (no-mime HEIC
  falls to extension, exactly as the reference).
- `displayName(fileName)` — a human title in place of a stored generated key
  (`9043cc23-…​.jpeg` → "JPEG image"), keeping a real name (`insurance-card.pdf`).
- `fileExtension(fileName, kind)` — the temp file's extension so the viewer picks
  the right renderer.

## Download-to-temp (`AsiApi`)

`downloadToTempFile` GETs the presigned URL and writes the bytes to a temp file
(QuickLook and PdfRenderer both need a local file, not a URL). **No bearer
token** — the presigned URL is itself the credential, the same rule the upload
PUT follows. The presigned URL is short-lived, so we download on open and never
cache it. (Kotlin takes the app cache dir; iOS uses `temporaryDirectory`.)

## Reader — the state machine (`GloveboxViewModel`)

`DocumentViewerState = idle | loading | ready(file,[kind,]title) | failed`.
`openDocument(doc, title, …)`:

- `unknown` kind → resolve the URL and call `openExternally` (the old behaviour) —
  never a broken preview.
- else → `loading` → download → `ready`, guarding against a dismiss mid-download
  (the temp file is deleted if the member already left).
- `dismissViewer()` deletes the temp file and returns to `idle`.

## Platform renderers

- **iOS** — `DocumentViewer.swift`: `QLPreviewController` wrapped for SwiftUI,
  presented as a `fullScreenCover`. Images (pinch/drag/rotate) and PDFs (pages,
  sharp zoom) for free, plus a Close button; dismiss returns to the Glovebox.
- **Android** — `DocumentViewer.kt`: a full-screen Compose overlay (last child of
  the Glovebox `Box`, with `BackHandler`). PDF → `PdfRenderer` draws every page
  to a bitmap sharp-to-width in a scrolling `LazyColumn` (rendered off the main
  thread). Image → `BitmapFactory` into a **pinch-zoom + pan** surface (the case
  that most needs zoom — a licence shot small). No new dependency.

## Deferral (honest)

Android **PDF** pages are sharp fit-to-width + vertical scroll but **not**
pinch-zoomable yet (images are). Pinch-zoom on a scrolling PDF is a gesture
conflict I chose not to rush; the pages render at 1600px so they stay legible.
iOS gets PDF zoom free from QuickLook. Noted as a follow-up; everything else of
Option A is in.

## Files

- Swift: `Core/Format/DocumentKind.swift`, `Core/Network/AsiApi.swift`
  (`downloadToTempFile`), `Feature/Glovebox/GloveboxViewModel.swift`,
  `Feature/Glovebox/DocumentViewer.swift`, `Feature/Glovebox/GloveboxScreen.swift`,
  `AttorneyShieldApp.swift`; tests `DocumentKindTests.swift`,
  `GloveboxViewModelTests.swift`.
- Kotlin: `core/format/DocumentKind.kt`, `core/network/AsiApi.kt`,
  `feature/glovebox/GloveboxViewModel.kt`, `feature/glovebox/DocumentViewer.kt`,
  `feature/glovebox/GloveboxScreen.kt`, `MainActivity.kt`; tests
  `DocumentKindTest.kt`, `GloveboxViewModelTest.kt`.

## Tests

`DocumentFile` kind/name (both platforms): pdf/image by mime & extension, no-mime
HEIC, unknown, generated-key → described, real name kept. Reader state machine
(both platforms): a PDF downloads to a temp file → `ready` with the field title,
never external; `unknown` opens externally and never enters the reader; a failed
download → `failed`; dismiss deletes the temp file.

- Swift: `DocumentKindTests` (7) + `GloveboxViewModelTests` (28, incl. 3 reader)
  → `** TEST SUCCEEDED **`.
- Kotlin: `DocumentKindTest` + `GloveboxViewModelTest` (3 reader) → **BUILD
  SUCCESSFUL**; full `assembleDebug` green (composable compiles).
