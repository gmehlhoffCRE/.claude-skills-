# Cresa — Visual Identity

> STATUS: **Color palette complete.** Logo and typography still pending (the source
> PDFs were read as text, which strips logos and fonts). Don't guess fonts or logo
> files — ask the user or use the brand guidelines. Color values below are official.

## Color palette

Color is a core part of Cresa's identity — inspired by the Cresa logo. The system is
built on **Midnight** and **Goldenrod** (primary) plus two grays, extended by three
secondary accents. Designed to be equally strong in digital and print.

### Primary colors

| Name | HEX | RGB | CMYK | Pantone | Role |
|---|---|---|---|---|---|
| **Midnight** | `#001E5A` | 0, 30, 90 | C100 M93 Y32 K33 | 2757 | Strong, grounding — anchors content; large color fields & backgrounds for text/imagery |
| **Goldenrod** | `#FFB600` | 255, 182, 0 | C0 M32 Y100 K0 | 1235 | Bright, eye-catching — **use in small amounts** to highlight/underscore key info, energize icons, guide the eye |
| **Dark Gray** | `#595959` | 89, 89, 89 | C63 M55 Y54 K28 | 424 | Neutral, versatile — spacing, structure, subtle callouts |
| **Light Gray** | `#E6E6E6` | 230, 230, 230 | C8 M6 Y7 K0 | 424 @ 15% | Backgrounds, dividers, subtle structure |

### Secondary colors (accents — use sparingly)

Add range and depth; a small pop to pull a design together. **Support** the primary
palette, never compete with it. A little goes a long way.

| Name | HEX | RGB | CMYK | Pantone |
|---|---|---|---|---|
| **Stadium Blue** | `#243E8C` | 36, 62, 140 | C100 M90 Y11 K1 | 286 |
| **Warm Orange** | `#FF8200` | 255, 130, 0 | C0 M60 Y100 K0 | 151 |
| **Bright Blue** | `#0056DA` | 0, 86, 218 | C86 M69 Y0 K0 | 2174 |

### Usage principles

- **Start with the primary palette and lean on white space.** Clean and sophisticated over busy.
- **Midnight = foundation/anchor.** Best for large color fields and backgrounds behind text or imagery.
- **Goldenrod = purposeful emphasis only.** Highlight key text, add energy to icons, guide the reader across the page. Keep it small.
- **Gray = neutral structure.** Define spacing, structure, and subtle callouts.
- **Secondary = intentional pops.** Guide the eye; keep the look unmistakably Cresa. Don't let accents overwhelm.

### Charts, graphs & dashboards

- **Start with the primary palette** (Midnight, Goldenrod, Gray); add secondary colors only as needed.
- **Solid flat fills** — avoid gradients within individual sections/segments.
- **Axis/grid lines:** light **gray**, thin weight; use gray strokes and backgrounds so the **metrics** stay the focus.
- **Tints for variety:** group similar shades for a natural cascade that guides the eye (e.g., place **Warm Orange next to Goldenrod**, blues together) for smooth transitions and less clutter.
- **Accessibility:** choose combinations with sufficient on-screen contrast (check with a color-contrast tool). Reflects Cresa's commitment to inclusivity.
- When building charts, also apply the `dataviz` skill's methods, but **swap its placeholder palette for the Cresa colors above.**

### Quick reference (for code / artifacts)

```css
:root {
  /* Primary */
  --cresa-midnight:   #001E5A;
  --cresa-goldenrod:  #FFB600;
  --cresa-dark-gray:  #595959;
  --cresa-light-gray: #E6E6E6;
  /* Secondary (accents) */
  --cresa-stadium-blue: #243E8C;
  --cresa-warm-orange:  #FF8200;
  --cresa-bright-blue:  #0056DA;
}
```

Suggested chart series order (primary first, then grouped accents):
`#001E5A` (Midnight) → `#243E8C` (Stadium Blue) → `#0056DA` (Bright Blue) → `#FFB600` (Goldenrod) → `#FF8200` (Warm Orange) → `#595959` (Dark Gray).

## Logo — TODO (awaiting assets)

- [ ] Primary logo (SVG + high-res PNG)
- [ ] Reversed / white version (for dark/Midnight backgrounds)
- [ ] Monochrome / single-color version
- [ ] Clear-space and minimum-size rules
- [ ] Misuse rules (don't stretch, recolor, add effects)
- [ ] Cresa Core™ lockup, incl. "Powered by CresaAI | Built on OpenAI"

Store files under `references/assets/` when provided.

## Typography — TODO (awaiting assets)

- [ ] Headline / display typeface (weights)
- [ ] Body typeface (weights)
- [ ] Web-safe / fallback stack
- [ ] Type scale and usage (H1/H2/body/caption)

## What to ask the user for next

The **official brand guidelines PDF** (or native template files) — for the **logo files,
fonts, and type scale**. Colors are now covered.
