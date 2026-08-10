# Attorney Shield — Colour System (Authoritative)

Source of truth: **`Attorney-Shield Color Scheme Review.pdf`** (Blue Sky Marketing).
This file is the machine-readable transcription of that PDF plus the contrast
analysis needed to apply it without shipping accessibility defects.

**Rule: every design in `kotlin` and `swift` uses these values. No other hexes.**

---

## 1. Authority order

When references disagree, resolve in this order:

| Rank | Source | Governs |
|---|---|---|
| 1 | **Colour PDF** (this file) | All colour values, without exception |
| 2 | **CodePen "Attorney - Shield App V6"** | Layout, typography, screen inventory, flow, look & feel |
| 3 | **`member-client`** | Behaviour, API contracts, state machines, error handling |

`member-client` is **not** a visual reference. Its CSS uses
`--asi-accent: #4f7cff` and `--asi-accent-2: #7a5cff` on a `#0b1020` base —
blue/violet, which the PDF explicitly lists under "colors to avoid" (Bright
Purple `#7B2FBE`: *"reads as tech startup or fintech, weakens the legal
authority signal"*). **Copy its logic, never its palette.**

### Known conflict: the CodePen palette differs from the PDF

The CodePen creative-direction card lists different values under different
names. The PDF wins on all four. Do not use the right-hand column.

| Role | PDF (use this) | CodePen (ignore) |
|---|---|---|
| Primary background | Shield Navy `#0D1B2E` | Protection Navy `#0D1B2E` — *same* |
| Secondary dark | Deep Navy `#122440` | Deep Navy `#0A1626` |
| Primary CTA | Justice Gold `#C4850A` | Signal Gold `#C4850A` — *same* |
| CTA hover | Active Gold `#E8A020` | Gold Highlight `#E8A020` — *same* |
| Success | Verified Green `#1E7A48` | Live Green `#2E9E5B` |
| Steel/blue | Mid Navy `#1A3A5C` + Steel Blue `#8DA8C4` | Trust Steel `#1A5FA8` |

The two golds and the primary navy agree, which is the important part — the
brand's CTA and hero colours are settled.

---

## 2. Primary palette

| Name | Hex | Role (per PDF) |
|---|---|---|
| Shield Navy | `#0D1B2E` | Primary background, hero sections, navbar |
| Deep Navy | `#122440` | Secondary dark sections, cards on dark bg |
| Justice Gold | `#C4850A` | Primary CTA buttons, accents, highlights |
| Active Gold | `#E8A020` | Hover/pressed states, badges, subtle icon fills |
| Off White | `#F5F4F0` | Page background for content sections |
| Pure White | `#FFFFFF` | Cards, content areas, pricing tables |

## 3. Supporting & functional

| Name | Hex | Role (per PDF) |
|---|---|---|
| Mid Navy | `#1A3A5C` | Borders on dark, dividers *(see §5 — not for text)* |
| Steel Blue | `#8DA8C4` | Muted text on dark backgrounds |
| Verified Green | `#1E7A48` | Success states, checkmarks, warranty badge |
| Charcoal | `#2A2A2A` | Body text on white, headings on light sections |
| Stone Gray | `#6B6A60` | Secondary body text, captions, fine print |

## 4. Forbidden

Never introduce these or anything near them:

| Avoid | Hex | Why (PDF) |
|---|---|---|
| Aggressive Red | `#FF4500` | Creates panic, not protection |
| Bright Purple | `#7B2FBE` | Reads tech-startup/fintech; weakens legal authority |
| Bright Teal | `#00B4D8` | Health/wellness territory; dilutes legal positioning |
| Flat Gray | `#F0F0F0` | Generic, no brand signal |

**Red is not banned for destructive/error semantics** — but derive an error
colour from the brand rather than reaching for `#FF4500`. Errors are a genuine
need (`member-client` has an `error` call phase); see §6.

---

## 5. Contrast analysis — binding rules

Computed WCAG 2.1 ratios. Normal text needs **4.5:1**; large text (≥18.66px
bold / ≥24px) and UI components need **3:1**.

### Passes — safe to use

| Foreground | Background | Ratio | Normal text |
|---|---|---|---|
| Pure White | Shield Navy | **17.31** | AAA |
| Pure White | Deep Navy | **15.53** | AAA |
| Active Gold | Shield Navy | **7.81** | AAA |
| Steel Blue | Shield Navy | **7.03** | AAA |
| Steel Blue | Deep Navy | **6.31** | AA |
| Justice Gold | Shield Navy | **5.53** | AA |
| Shield Navy | Justice Gold | **5.53** | AA |
| Shield Navy | Active Gold | **7.81** | AAA |
| Charcoal | Active Gold | **6.48** | AA |
| Charcoal | Off White | **13.04** | AAA |
| Charcoal | Pure White | **14.35** | AAA |
| Pure White | Verified Green | **5.34** | AA |
| Stone Gray | Off White | **4.95** | AA |
| Charcoal | Justice Gold | **4.58** | AA |

### Failures — these are the traps

| Foreground | Background | Ratio | Verdict |
|---|---|---|---|
| **Pure White** | **Justice Gold** | **3.13** | ❌ Fails AA for normal text |
| **Pure White** | **Active Gold** | **2.22** | ❌ Fails outright |
| **Mid Navy** | **Shield Navy** | **1.49** | ❌ Invisible as text |
| **Justice Gold** | **Off White** | **2.85** | ❌ Fails, even large |
| Active Gold | Pure White | 2.22 | ❌ Fails outright |

### The three rules that follow

**R1 — Never put white text on either gold.**
The PDF's own live-site preview shows a gold "Get Protected" button with white
text at 3.13:1. Reproducing that ships a WCAG failure on the single most
important CTA in the app. **Use Shield Navy `#0D1B2E` on gold (5.53:1).**
Navy-on-gold also reads as more premium than white-on-gold.

**R2 — Mid Navy `#1A3A5C` is a border colour only.**
The PDF lists it as "borders on dark, dividers, *secondary text on dark*". As
text on Shield Navy it is 1.49:1 — effectively invisible. For secondary text on
dark, use **Steel Blue `#8DA8C4`** (7.03:1), which the PDF itself assigns to
"muted text on dark backgrounds". Treat the "secondary text" part of the Mid
Navy note as an error in the source document.

**R3 — Gold is never body text on light backgrounds.**
`#C4850A` on Off White is 2.85:1. Gold on light is reserved for large display
type and decorative accents. For emphasis in light sections use Charcoal.

---

## 6. Semantic tokens

Define these once per platform; reference tokens in UI code, never raw hex.

| Token | Value | Notes |
|---|---|---|
| `bgPrimary` | `#0D1B2E` | App/hero background |
| `bgSecondary` | `#122440` | Cards & sections on dark |
| `bgPage` | `#F5F4F0` | Light content background |
| `surface` | `#FFFFFF` | Cards on light |
| `ctaBg` | `#C4850A` | Primary button fill |
| `ctaBgPressed` | `#E8A020` | Pressed/hover fill |
| `ctaFg` | `#0D1B2E` | **Text on CTA — navy, per R1** |
| `textOnDark` | `#FFFFFF` | Primary text, dark bg |
| `textOnDarkMuted` | `#8DA8C4` | Secondary text, dark bg (R2) |
| `textOnLight` | `#2A2A2A` | Primary text, light bg |
| `textOnLightMuted` | `#6B6A60` | Captions, fine print |
| `borderOnDark` | `#1A3A5C` | Dividers on dark — **never text** |
| `success` | `#1E7A48` | Verified/connected; white text OK |
| `accentOnDark` | `#E8A020` | Gold text/icon on dark (7.81:1) |

**Deliberately unresolved: `danger`.** The call flow needs an error state and a
hang-up affordance, and the PDF supplies no error colour while forbidding
`#FF4500`. Do not invent one silently — this is an open question for Blue Sky
Marketing (see the development plan's open-questions section). Interim: render
error *text* as Charcoal/White on the normal background with a Verified-Green-
free icon, and style hang-up as a neutral outlined control, so nothing ships in
an unapproved colour.

## 7. Typography (CodePen)

Family **Inter**, one family across the whole app:

| Role | Weight | Treatment |
|---|---|---|
| Display | 800 | Tight tracking |
| Title | 700 | — |
| Body | 500 | — |
| Eyebrow | 800 | All caps, letter-spaced |

Map to platform scales rather than hard-coding pt/sp, so OS font-size
accessibility settings are respected.

## 8. Product principles (CodePen — carry into every screen)

1. Minimize friction before purchase — ask only what's required to take payment.
2. Defer everything non-critical to after activation, handled with gentle nudges.
3. Make payment terms and renewal timing explicit, never buried.
4. Guided nudges, never hard stops — members can skip and return.
5. One job per screen; the attorney button is always the hero.
