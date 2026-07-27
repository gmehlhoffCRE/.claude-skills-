# Cresa — Visual Identity

> STATUS: **Color palette complete. Primary (color) logo delivered** — official EPS +
> web SVG/PNG/PDF in `references/assets/`, plus full usage rules. Still pending: the
> **reversed/white** logo variant and **typography** (fonts). Don't guess fonts — ask
> the user or use the brand guidelines.

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

## Logo

**Usage rules are complete; the artwork FILES are still outstanding** (need the actual
SVG/PNG assets — see checklist at the end of this section).

**Meaning & integrity.** The logo tells Cresa's story — every detail is intentional.
Each **yellow (Goldenrod) square** represents Cresa's values, benefits, and services.
All elements work together seamlessly, so **always use the correct, approved artwork.**

**Never:**
- Separate the logotype from the mark.
- Change the colors, sizes, or construction of any element.
- Stretch, distort, recolor, or add effects.
- Put a **shadow** behind the logo.

**Clearspace.** Keep clear space around the logo equal to **2× the height or width of the
"C"** in the logotype. This keeps the logo from competing for attention.

**Color variations (for legibility on any background):**
- **Light backgrounds →** use the **standard** logo.
- **Dark backgrounds →** use the **white** logotype.
- **Over an image →** place it on an area with enough calm space and contrast. If the
  layout doesn't give the right balance, **adjust the background, not the logo** — never
  add a shadow or alter the mark.

**Artwork files (in `references/assets/`):**

*Primary logo — wide/horizontal, standard (color):*
- `Cresa_Logo_Primary_wide.eps` — **official source vector** (Adobe Illustrator; authoritative for print).
- `Cresa_Logo_Primary_wide.svg` — vector for **web/artifacts**; fills normalized to brand hex (`#001E5A` / `#FFB600`); validated in Chromium.
- `Cresa_Logo_Primary_wide.png` — transparent, 2003×346, brand hex; for slides/docs/raster.
- `Cresa_Logo_Primary_wide.pdf` — vector PDF (from the EPS).

> The SVG/PNG/PDF are derived from the official EPS. The EPS is the source of truth;
> for any high-stakes print use, prefer the EPS (or request the native AI file).

*Still needed (request from brand team):*
- [ ] **Reversed / white** version (official) — for dark/Midnight backgrounds. *(Do not fabricate; use official artwork.)*
- [ ] Monochrome / single-color version (if used).
- [ ] Stacked/vertical and icon-only (squares) lockups, if they exist.
- [ ] **Cresa Core™** lockup, incl. "Powered by CresaAI | Built on OpenAI".

## Typography — TODO (awaiting assets)

- [ ] Headline / display typeface (weights)
- [ ] Body typeface (weights)
- [ ] Web-safe / fallback stack
- [ ] Type scale and usage (H1/H2/body/caption)

## What to ask the user for next

The **official brand guidelines PDF** (or native template files) — for the **logo files,
fonts, and type scale**. Colors are now covered.
