# 2026-09-09 — Home sponsor-banner carousel (member-client parity)

Samson spotted (screenshot) an auto-rotating "SPONSORED" card carousel below the
Protection-readiness tracker on member-client's Home that our apps didn't show,
and asked to add it.

## What it is

A backend-driven advertisement carousel (member-client `contentApi.ts` +
`SponsorBanners.tsx`). I confirmed it's live: `sponsorBannersByOrganization` for
this dev org returns one banner ("Attorney Shield" → attorney-shield.com) with a
**3-image gallery** (onetap / protection / scales), which member-client flattens
into 3 slides — hence the 3 pagination dots in the screenshot. Our apps had **zero**
sponsor-banner support.

## Shipped both apps (kotlin e5c7d36 / swift 8ed20dc)

- **Network** (`ContentModels` + `AsiApi.listSponsorBanners`): query
  `sponsorBannersByOrganization(org){ id title clickThroughUrl imageFilePath images{imageFilePath} }`,
  flattening a multi-image banner into one `SponsorBanner` per image (gallery
  preferred, legacy `imageFilePath` as fallback). Best-effort — empty list on any
  failure so a content hiccup never blocks Home. A faithful port of
  `listSponsorBanners`.
- **UI** (`SponsorBanners`): Android `HorizontalPager` + Coil `AsyncImage`; iOS
  `TabView(.page)` + `AsyncImage`. Auto-advance every 5s, pagination dots +
  tap-to-open when >1 slide, static with one. A "Sponsored" tag overlays each
  slide. Placed at the **foot of Home**, gated on `canCall && banners nonempty`
  (paying member with banners) — matching member-client's `showBanners`.
- **Open**: Android via `Intent(ACTION_VIEW)`; iOS via `@Environment(\.openURL)`.

## Tests / verification

3 new `AsiApi(Test|Tests)` each side — flatten multi-image, legacy single-image
fallback, empty-on-failure. Android `:app:testDebugUnitTest` green; iOS
`xcodebuild test` (AsiApiTests + HomeViewModelTests) **TEST SUCCEEDED**.

## Notes / tunables

- Banner aspect is a constant (Android `BANNER_ASPECT = 3.1`, iOS `bannerHeight =
  118`) — the images are designed to fill; easy to tune once seen on device.
- Coil was already a dependency (from the profile-photo work); no new Android dep.
- The 5s auto-advance is unconditional on iOS (SwiftUI can't easily detect a
  mid-drag to pause like member-client does); minor fidelity difference.
