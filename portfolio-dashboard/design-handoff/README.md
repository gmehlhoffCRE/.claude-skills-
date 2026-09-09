# Handoff: Rimkus Real Estate Portfolio Dashboard (Google Sheets–driven)

## Overview
An internal portfolio-management dashboard for a corporate real estate director (built by Cresa for its client Rimkus). It maps a global lease portfolio (~60 leases) and surfaces the metrics a director needs to manage it: lease expirations, occupancy costs, footprint, active transactions, and advisor notes.

**Core requirement: NO location data may be hard-coded.** Every lease record must be read from a Google Sheet at load time so the client can maintain the portfolio in the sheet and see the dashboard update without code changes. The bundled `portfolio-data.sample.js` is seed/reference data only — use it for local dev fixtures and to understand the shape of real data, never ship it as the data source.

## About the Design Files
The files in this bundle are **design references created in HTML** — prototypes showing intended look and behavior, not production code to copy directly. Recreate them in the target codebase's environment and patterns; if no codebase exists yet, choose an appropriate modern stack (e.g. React + Vite, or Next.js) and implement there.

- `Rimkus Portfolio Dashboard.dc.html` — the full dashboard (four views). The `<x-dc>` template section shows all markup/styling inline; the `<script data-dc-script>` class shows all derived-metric computation.
- `portfolio-map.html` — the interactive world map (d3-geo + TopoJSON), embedded via iframe in the prototype. In production, render it as a component, not an iframe.
- `portfolio-data.sample.js` — the record schema + 60 sample rows.
- `assets/Cresa_Logo_Primary_wide.svg` — header logo.

## Fidelity
**High-fidelity.** Colors, typography, spacing, and layout are final and follow the Cresa brand system. Recreate pixel-perfectly.

## Data Architecture (build this first)

### Google Sheet as the single source of truth
One sheet ("Portfolio"), one row per lease, columns exactly matching the client's existing "Real Estate Portfolio Summary" workbook:

| Column | Type | Notes |
|---|---|---|
| LEASE TYPE | enum | Direct Lease / Sublease / Exec Suite |
| REGION | enum | West / Southeast / South Central / Northeast / Canada / International |
| TRANSACTION STATUS | enum | Active / Inactive (Active = open transaction) |
| OPERATING SEGMENT | enum | Forensics, BES, Life Sciences, Corporate, Corp/Forensics, BES/Forensics, EMEA, APAC |
| LEASE CITY | string | |
| ST | string | state / province / country code |
| STREET ADDRESS | string | |
| PROPERTY TYPE | enum | Flex / Office / Warehouse / Exec Suite |
| SF | number | rentable square feet |
| LEASE EXP | date or "MTM" | source workbook uses Excel serial dates — convert `new Date(Date.UTC(1899,11,30) + serial*86400000)`; also accept ISO/formatted dates; "MTM" = month-to-month |
| ANNUAL GROSS RENT ($US) | number | |
| CRESA NOTES | string | free text; drives Needs Attention + Pipeline copy |
| LAT | number | add these two columns to the sheet |
| LNG | number | (or geocode server-side and cache; do NOT geocode client-side per load) |

### Access pattern
Preferred: Google Sheets API v4 (`spreadsheets.values.get`) with an API key restricted to the sheet, or a service account if the sheet must stay private. Acceptable fallback: publish-to-web CSV (`.../gviz/tq?tqx=out:csv`) fetched client-side. Either way:
- Fetch on load; show a loading state; cache last-good response (localStorage) and render it with a "stale data" indicator if the fetch fails.
- Show a data-source status chip in the header: green dot + "LIVE · {n} LEASES · {AGR} AGR" when fresh; amber variant when serving cached/fallback data.
- All KPIs, charts, map dots, and tables must be **computed from the fetched rows** — nothing pre-aggregated in code. Derived per-row: `psf = agr / sf`; expiration bucket by calendar year; "expiring soon" = expDate < today + N months (N configurable, default 12).

## Screens / Views
Four views switched by header tabs (Overview / Expirations / Pipeline / All Sites). Shell shared by all views:

### Shell
- Page background `#F4F5F8`; font `Arial, Helvetica, sans-serif` everywhere; **square corners (border-radius 0) on every element**.
- **Header** (sticky, white, min-height 62px, bottom border `#E6E6E6`, padding 10px 24px, flex-wrap): Cresa logo (20px tall) · 1px divider · title "RIMKUS REAL ESTATE PORTFOLIO" (14px/700 `#001E5A`, uppercase, nowrap) with subtitle "OCCUPIER PORTFOLIO MANAGEMENT · AS OF {date}" (9.5px/700 `#8A93A8`, letter-spacing 1.4px, truncates) · spacer · live-data chip · view tabs.
- **Tabs**: 32px tall buttons, 12px/700; active = navy `#001E5A` bg, white text; inactive = white bg, `#E6E6E6` border, `#333` text.
- **KPI band** (grid auto-fit minmax(150px,1fr), gap 12px, padding 16px 24px 0): white cards with **3px solid `#FFB600` top border**, `#E6E6E6` other borders, padding 12px 14px. Value 23px/700 `#001E5A`; label 9.5px/700 `#595959` uppercase ls 1px; sub-line 10.5px `#8A93A8`. Six KPIs, all computed: Locations · Total Footprint (SF) · Annual Gross Rent · Avg Rent/SF · Expiring ≤ N mo (count, with SF + AGR sub) · Active Transactions.

### 1 · Overview
Content padding 14px 24px 28px, vertical gap 14px.
- **Row 1** — grid `minmax(0,1.55fr) minmax(280px,1fr)`, gap 14px:
  - **Global Footprint map card** (left): card header (11px/700 navy uppercase title + muted hint "dot size = SF · gold ring = active transaction · click a dot for detail"); map fills remaining height (min 472px). Map spec below.
  - **Right rail**: (a) **SF Expiring by Year** — vertical bar chart, one bar per year 2026→2031 + "2032+", bars `#001E5A` except 2032+ in `#FFB600`, value labels above bars (10px/700 `#595959`), year labels below a 1px divider, footnote 10.5px `#8A93A8`; (b) **donut card** — two-column grid: "Annual Rent by Segment" and "SF by Property Type". Donuts are 158px conic-gradient circles with a white center hole (inset 34px) showing total ($8.04M AGR / 324K SF at 18px/700 navy). Legends below: 9px color square, name, value (700 navy), percent (`#8A93A8`).
- **Row 2** — same outer grid as Row 1 so edges align; left cell is an inner auto-fit grid holding **Rent & Footprint by Region** and **Largest Commitments**; right cell is **Needs Attention**. All three cards stretch to equal height (flex column, content `justify-content:space-between`).
  - **Rent & Footprint by Region**: one row per region, grid `110px 1fr 120px`: region name (12.5px/700 `#333`) with muted "n sites · SF" line beneath; horizontal bar (8px tall, track `#EEF0F4`, fill = region color, width ∝ AGR vs max region); right column AGR (13px/700 navy) with muted "$xx.xx /SF" beneath. Only name + AGR are bold.
  - **Largest Commitments**: top 5 by AGR. Rank badge 22px navy square with white number; city (12.5px/700), address · segment · SF muted line; right-aligned AGR (700 navy) + expiration (muted).
  - **Needs Attention**: rows flagged from CRESA NOTES containing close/sublease keywords. Chip (uppercase 9px/700, square): "CLOSING" = white bg / `#C93B3B` text+border; "SUBLEASE" = `#FFB600` bg / navy text. City + muted meta, note text 11px `#595959`.

### 2 · Expirations
Grid `minmax(0,1fr) 210px`, gap 14px.
- **Lease Expiration Runway** (left card): header with legend (gold = active transaction, navy = no action yet, red `#C93B3B` = closing at expiration). Scrollable table, min-width 960px, grid `190px 1fr 76px 70px 84px`: Location | timeline track | Expires | SF | AGR. Timeline axis spans "today" → ~66 months out, year tick labels ('27…'32) positioned proportionally. Each lease renders a 12px-tall bar from x=0 to its expiration date (min width 1.5%, clamped at 100% with a "→ {date}" tail label for leases beyond the window; MTM leases get a stub bar labeled "MTM"). Rows zebra-striped `#FAFBFD`. Expiration dates within the "expiring soon" window render `#B54708`.
- **By Expiration Year** (right rail): heading + one compact card per year: 3px left accent (`#FFB600` for the first two years, navy after), year label, "{n} lease(s)" (18px/700 navy — singular/plural correct), right-aligned "SF / AGR" muted two-line block.

### 3 · Pipeline
Single full-width card: "Active Transaction Pipeline · {n} open transactions · sorted by expiration". Navy `#001E5A` header row (10px/700 white uppercase), columns `180px 90px 80px 90px 1fr`: Location (city 12.5px/700 navy + address muted) | Expires (700, `#B54708` when soon) | SF | AGR | Status/Next Step (the CRESA NOTES text, 11.5px `#595959`). Zebra rows, hover `#F4F7FC`. Contains only rows with TRANSACTION STATUS = Active.

### 4 · All Sites
Full data table.
- Toolbar: "ALL SITES · {shown} of {total}" · search input (32px, `#F8F9FB` bg, filters city/address/segment/region/type/notes) · region filter pills (28px; active = navy bg white text) · right-aligned live totals of the filtered set ("Filtered: {SF} SF · {AGR} AGR · click headers to sort").
- Table (h-scroll, min-width 1280px, sticky navy header): columns City/Market · Region · Segment · Prop Type · Lease Type · Street Address · SF (right) · Expires · Annual Rent (right) · $/SF (right) · Status · Cresa Notes (wraps). Every header sorts (toggle asc/desc; numeric columns default desc); active sort header shows ▴/▾ in `#FFB600` on `#14316B` bg. City cell 12px/700 navy; expiring-soon dates `#B54708`; Status chip "ACTIVE" gold/navy or "—" muted. Zebra `#FAFBFD`, hover `#F4F7FC`.

## Map spec
- Real geometry only: TopoJSON world (`world-atlas@2` countries-110m, Natural Earth) via d3-geo, `geoNaturalEarth1` projection, Antarctica excluded/cropped. Land `#E6E6E6` with white 0.6px strokes on `#F4F7FC`.
- One circle per lease at LAT/LNG: radius = sqrt scale on SF (range ~2.5–17px), fill = region color at 0.78 opacity, stroke white 1px — **except Active transactions: `#FFB600` stroke 2px**. Larger dots drawn first.
- Hover tooltip (navy bg, white text, 11.5px): city/state, address, segment · type · SF, AGR, expiration (gold), "ACTIVE TRANSACTION" flag.
- Click → detail panel (288px, top-right of map, white, `#E6E6E6` border, large soft shadow): property name (15px/700 navy), address, 2-column field grid (Operating Segment, Region, Property Type, Lease Type, Rentable SF, Expires, Annual Gross Rent, Rent/SF, Transaction), and a "CRESA NOTE" callout on `#F4F7FC` when notes exist. × button and click-away close it.
- Legend chip row bottom-left: region color dots + names.

## Interactions & Behavior
- Tab switching preserves state; default view Overview. Make the expiring-soon window (default 12 mo) a configurable constant/setting.
- Table sorting, text search, and region filter combine; filtered totals recompute live.
- Hovers: rows → `#F4F7FC`; buttons/pills → border `#8A93A8` or navy-step; keep motion minimal (150ms color/opacity steps only). Link color `#0056DA`.
- Loading: skeleton or quiet placeholders while the sheet fetch resolves; error → cached data + amber chip.

## Design Tokens
- Midnight (primary) `#001E5A` · navy hover step `#14316B` · Goldenrod accent `#FFB600` · Stadium Blue `#243E8C` · Bright Blue `#0056DA` · Warm Orange `#FF8200` · Dark Gray text `#595959` · muted `#8A93A8` · body text `#1a1a1a`/`#333` · borders `#E6E6E6` · hairlines `#EEF0F4` · page bg `#F4F5F8` · zebra `#FAFBFD` · hover wash `#F4F7FC` · danger `#C93B3B` · warn (expiring) `#B54708` · ok `#1B8F6A`.
- Region colors (map dots = region bars): West `#0056DA` · Southeast `#FF8200` · South Central `#001E5A` · Northeast `#243E8C` · Canada `#595959` · International `#FFB600`.
- Segment colors: Forensics `#001E5A` · BES `#243E8C` · Corp/Forensics `#0056DA` · APAC `#FFB600` · EMEA `#FF8200` · Life Sciences `#595959` · BES/Forensics `#8A93A8` · Corporate `#C5CBD6`.
- Property-type colors: Flex `#0056DA` · Office `#001E5A` · Warehouse `#FF8200` · Exec Suite `#FFB600`.
- Type: Arial only; hierarchy by weight/size; card titles 11px/700 uppercase navy, letter-spacing 1px; table headers 10px/700 uppercase white on navy; data 11.5–13px. Number formatting: `$8.04M` / `$130K`, SF as `324K` / `8.7K`, dates `Sep '26`, tabular-nums on numeric columns.
- Radius 0 everywhere. Spacing: 24px page gutters, 14px card gaps, 12–18px card padding.

## Brand rules (Cresa)
Never recolor/stretch the logo or separate the wordmark from its squares; white logo on dark, primary on light. No emoji. Gold used sparingly for emphasis only. Uppercase display headers.

## Assets
- `assets/Cresa_Logo_Primary_wide.svg` (official).
- Icons if needed: Lucide, stroke 1.5–2, Midnight (no official icon set exists).

## Future roadmap (design for, don't build yet)
Headcount per site (→ cost-per-seat, SF/person KPIs), rent escalations/obligation curve, market benchmarking, budget vs actual. Keep the record schema extensible.
