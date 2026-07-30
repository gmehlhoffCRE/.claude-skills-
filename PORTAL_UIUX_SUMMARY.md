# Cresa Client Portal — UI/UX Restyle Summary

Working branch: `claude/html-ui-ux-review-s975dj`

Two files:
- **`portal-restyled.html`** — the real, gated portal (opens only with a valid `?s=<token>` link).
- **`portal-preview.html`** — a review-only copy hardwired to preview mode. **Double-click to open** (no link/token, no URL suffix). Loads baked-in sample data; Firebase is never touched.

> To review: open `portal-preview.html`, look for the **PREVIEW** badge by the logo. External CDNs (React/Babel/Firebase/Google Fonts) must load, so open it on a normal internet connection.

---

## Design system

- **Typography → Inter everywhere.** All three type tokens (`--sans`, `--serif`, `--mono`) now resolve to Inter, so the app is a single typeface. Loaded the 700 weight; fallback stack is `Inter → Helvetica Neue → Helvetica → Arial`.
  - ⚠️ **Brand note:** Cresa's official typeface is **Arial**. Inter is off-brand but was an explicit product choice for a more modern feel. One commit reverts it if brand compliance is required.
- **Brand colors preserved.** Midnight `#001E5A` and Goldenrod `#FFB600` are untouched (an early brass retune was reverted).
- **Motion:** shared easing token, subtle hover-lift on cards/buttons, staggered dashboard entrance, full `prefers-reduced-motion` fallback.
- **Focus:** crisp Midnight `:focus-visible` rings on interactive elements.
- **Elevation:** richer, Midnight-tinted layered shadows.
- **Accessibility:** darkened the lightest neutral gray for small-label contrast.
- **Wider shell:** content max-width routed through one `--shell-max` token (1880px).

---

## Map / survey-list view

- Property-card stats reduced to **SF range · Total Asking Rent · Availability** (removed Lease Type; SF is a min–max range like the rent range).
- Fixed text clipping in the list column.

---

## Compare matrix

- Neutral, single-font styling (no bluish text); tabular figures.
- **All building-detail data points** derived from the records (building specs + suite-level min–max ranges).
- Row order (trimmed): Submarket · Building Class · Year Built/Renov · Stories · Percent Leased · Premises SF · Base Rent/SF · Est. OpEx/SF · Total Rent/SF · Monthly Rent · Parking Ratio · Parking $/Space/Mo · Landlord · **Shortlist/Remove**.
- **Subtle zebra**, **left-aligned** cells, uniform **12px** font.
- **Full-width navy header band** (photo row + a continuous navy name/address band) to anchor the table; building photo left-aligned.
- **Lease Type = Direct/Sublease** (Full Service/NNN relabeled "Lease Structure").

---

## Building detail page

- **Title bar:** gold submarket pill (top-left) + compact **"Map"** button (top-right, matched to the pill); smaller building name, larger address; **← Building N of M →** pager on the address line. (Summary strip and X-close were removed per feedback.)
- **Left column ("Building Info"):** mini-map on top, ordered spec list (Class, Year Built/Renov, Stories, Total Building Area, % Leased, Parking Ratio, Parking $/Space/Mo, Landlord) with a "Notes" block below (underlined header).
- **Center (photo + data):** hero photo (420px) with a **vertical thumbnail rail** to its right; the photo row spans the full center width and lines up with the table below. Gradient scrim keeps the photo counter legible.
- **Available spaces table:** one row per suite, **sorted by floor (low→high)**, neutral uniform cells, fixed even columns, **Premises SF** as its own column, a button-styled **floor-plan icon** per row. Columns: Suite · Premises SF · Base Rent/SF · Est. OpEx/SF · Total Rent/SF · Monthly Rent · Lease Type · Term.
- **Right rail (pinned action panel):** **Vote** (segmented Shortlist/Remove), **Comments** (live thread + composer), **Attachments** (uploaded docs) — always visible.
- **Mobile:** suite table collapses to stacked cards; hero/thumbnails stack.

---

## Data-model hooks added (portal side ready; generator must supply)

Optional fields the portal now reads (default gracefully when absent):
- `parkingReserved` / `parkingUnreserved` → "Parking $/Space/Mo"
- `percentLeased` → "Percent Leased"
- `dealType` (per suite: Direct/Sublease) → "Lease Type" (defaults to "Direct")
- `documents` (array of `{label, type, url}`) → Attachments (flyers, RFP responses, etc.)

**Computed value flag:** "Monthly Rent" is calculated client-side (Total Rent/SF × SF ÷ 12). This is the one spot the portal does display-time math, contrary to the "strings stay strings" build rule. Consider a stored generator value, and label it "est."

---

## Open items / pending decisions

1. **Compare vote buttons** — recommended: move thumb-up/down icons into the navy header band (per building), drop the bottom row. *(Not yet done — awaiting go-ahead.)*
2. **"est." marker** on the computed Monthly Rent.
3. **"—" → "Incl."** for Full-Service suites with no separate total rent.
4. **Formal accessibility audit** — `scope="col"` on headers, table caption, keyboard-focus pass.
5. **Typography** — confirm Inter vs. reverting to brand-standard Arial.
