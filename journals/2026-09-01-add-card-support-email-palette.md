# 2026-09-01 — Add-card screen: support email was the forbidden blue (iOS)

## What I was asked

"Check out the Add card screen." (Screenshot: the "Card entry is not available"
placeholder, with `support@attorney-shield.com` rendered in **blue**.)

## The bug

On iOS, a bare email in a plain `Text("… support@attorney-shield.com.")` is parsed
as markdown and **auto-linked**, and a link ignores `foregroundStyle` — it takes
the environment tint, which defaults to **system blue (~#4f7cff)**. That's exactly
the member-client blue the palette forbids ("its CSS is blue/violet — the *avoid*
territory; accent is Justice Gold, or navy on light"). Android's Compose `Text`
does **not** auto-link, so it showed the email as plain muted text — so the two
platforms also disagreed.

Two places hit this on iOS: the **Add card** pane, and any **`AsiTextField`
supporting text** carrying an email (e.g. the change-email screen's
"contact Support at support@attorney-shield.com").

## Fix

Two contexts, each made consistent across platforms:

- **Add card screen — a proper gold, tappable `mailto:` link** (on-palette +
  useful). iOS: an explicit markdown link with `.tint(accentText)` so the link is
  Justice Gold, not blue. Android: a `buildAnnotatedString { withLink(
  LinkAnnotation.Url("mailto:…", TextLinkStyles(SpanStyle(color = accentText)))) }`
  — a gold tappable link too (Compose 1.7 link API; BOM 2024.10).
- **Shared `AsiTextField` supporting text (iOS)** — render `Text(verbatim:)` so a
  bare email/URL is **not** auto-linked to blue; it stays plain muted helper copy,
  matching Android. Systemic: fixes the change-email screen and any future
  supporting text. (Android supporting text already renders plain; no change.)

## Files

- Swift: `Core/Design/AsiComponents.swift` (`AsiTextField` supporting text →
  `verbatim`), `Feature/Account/AccountScreen.swift` (Add-card gold mailto link).
- Kotlin: `feature/account/AccountScreen.kt` (Add-card gold mailto link).

## Tests / build

No new unit tests — this is presentation-only (a colour + link treatment).
Compilation is the check.

- Swift: app builds (`BirthDateTests` run → `** TEST SUCCEEDED **`).
- Kotlin: `compileDebugKotlin` → **BUILD SUCCESSFUL**.

Worth an on-device glance on both: confirm the email now reads gold and opens the
mail composer, and that no other placeholder/helper copy still shows a blue
auto-link.
