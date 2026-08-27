# 2026-08-27 — Glovebox empty for a trial account: `image` fields dropped

## Symptom

x1 (a Uganda-org trial account) saw an empty Glovebox — "No document sections are
configured yet" — despite the org having a document section. Reported as "glovebox
isn't loading things for this account."

## Diagnosis (captured live on the emulator via added logging)

```
AsiGlovebox: raw fields: National ID:image
AsiGlovebox: load · sections=1 fields=1 memberInputFields=0 shownSections=0
```

x1's org has one section and one field — **"National ID", type `image`**. The
Glovebox only shows sections that have a *member-input* field, and
`DocumentFieldKind.fromWire` mapped **`image` → `Unsupported`** (not member input),
so the only field was dropped and the section vanished.

The `image → Unsupported` mapping was a past guess: a comment noted the only dev
`image` field belonged to an org "Policy" template, so `image` was excluded to
keep templates out of the member's Glovebox. That guess is wrong — "National ID"
is a genuine member document, and **`member-client` treats `file` and `image`
identically** ("upload-bearing types (file/image) use the S3 widget";
`DocumentsScreen` offers camera/gallery/file for any upload field).

## Fix

Map **`image` → `File`** (a member upload) on both platforms
(`core/network/DocumentModels.*` `DocumentFieldKind.fromWire`). The field type
describes the *document*, not the file format, so an `image` field is a member
upload like `file`.

**Verified live on the emulator** (x1 signed in): the Glovebox now shows a
"National ID" section ("0 of 1 sections on file", with an **Add** action) instead
of the empty state — `load · … memberInputFields=1 shownSections=1`.

## Also added

Diagnostic logging (kept — low-noise, one line per Glovebox load): the raw field
`title:type` list (`AsiApi.listDocumentFields`) and the load summary
(`sections/fields/memberInputFields/shownSections`, `GloveboxViewModel`). This is
what pinned the cause and will surface the next unrecognised `type` — the backend
`type` vocabulary is still only partly known (`text/dropdown/file/image` mapped;
`textarea/number/date/radio/checkbox` still fall through to `Unsupported`).

## Tests

Updated `GloveboxViewModelTest(s)` on both platforms: the fixture now models
"National ID" (`image`) as its own member section that shows, while the "Policy"
template (a `policy`-type field) stays hidden; the old "image is not a member
upload" test is now "image is a member upload and its section shows". Android
suite green; iOS `TEST SUCCEEDED`.

## Follow-up (flagged, not done)

- The other admin `type`s member-client supports (`textarea/number/date/radio/
  checkbox`) are still `Unsupported` here — they'd need input widgets. If an org
  configures one, its section would vanish the same way. The logging will catch it.
- The `File` upload path should accept photos (camera/gallery) for `image` fields,
  as member-client does — worth confirming the app's picker isn't document-only.
