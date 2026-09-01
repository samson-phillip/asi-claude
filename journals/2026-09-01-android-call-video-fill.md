# 2026-09-01 — Android live call: video now fills the screen (parity with iOS)

## Symptom

On Android the attorney's live video was **letterboxed** — shown in a band in the
middle of the screen with black bars top and bottom — while iOS fills the screen
with the controls floating on top.

## Cause

Not a layout problem: the Compose `LiveState` is already a full-screen `Box` with
the video `AndroidView` at `fillMaxSize` and the header / self-view / controls
floating over it, and `attachOnce` adds the OpenTok view `MATCH_PARENT`. The
letterbox came from the **OpenTok renderer scale mode**: Android's default is
*fit* (letterbox), whereas OpenTok **iOS** defaults subscribers/publishers to
*fill* (crop) — which is why iOS filled and Android didn't.

## Fix (`kotlin`, `VonageSession.kt`)

Set the renderer to crop-to-fill on both streams:

```
setStyle(BaseVideoRenderer.STYLE_VIDEO_SCALE, BaseVideoRenderer.STYLE_VIDEO_FILL)
```

- Subscriber (attorney video) → fills the full screen, no black bars.
- Publisher (self-view) → fills its PiP card.

Trade-off (same as iOS): a landscape feed is cropped at the sides to fill a
portrait screen — the definition of "fill the screen."

## Verified

- `assembleDebug`/`installDebug` green on both devices.
- User confirmed on device: the video now fills the screen with the components
  floating on top, matching iOS.

## Files

- `kotlin/app/src/main/java/com/attorneyshield/member/core/video/VonageSession.kt`
