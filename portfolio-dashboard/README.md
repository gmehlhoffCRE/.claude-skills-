# Rimkus Real Estate Portfolio Dashboard

An internal portfolio-management dashboard for a corporate real estate director, built by Cresa
for its client Rimkus. It maps a global lease portfolio and surfaces what a director manages
day to day: expirations, occupancy cost, footprint, active transactions, and advisor notes.

**Google Sheets is the single source of truth.** No lease or location data exists in this
codebase. Every KPI, chart, map dot, and table row is computed at runtime from rows fetched out
of one sheet, so the client maintains the portfolio in the spreadsheet they already use and the
dashboard follows without a code change. → [SETUP.md](SETUP.md)

## Quick start

```bash
npm install
VITE_USE_FIXTURE=true npm run dev     # sample data, no sheet required
```

To point at a real sheet, copy `.env.example` to `.env.local`, set `VITE_SHEET_ID`, and run
`npm run dev`. [SETUP.md](SETUP.md) walks through creating the sheet, sharing it, and publishing
the app.

## Views

| View | What it answers |
|---|---|
| **Overview** | Where is the portfolio, what does it cost, and what needs attention? World map with clickable property detail, SF expiring by year, rent by segment, SF by property type, rent and footprint by region, largest commitments, and a Needs Attention list driven by Cresa notes. |
| **Expirations** | What is coming due and when? A runway timeline (one bar per lease, colored by closing / active transaction / no action) plus a by-year rail with lease counts, SF, and rent. |
| **Pipeline** | What is in flight? Every lease with `TRANSACTION STATUS = Active`, sorted by expiration, with the Cresa note as the next step. |
| **All Sites** | Everything, filterable. Sortable 12-column table with text search, region pills, and live totals for the filtered set. |

## Architecture

```
src/
  config.ts            env-driven settings (sheet id, tab, key, expiring window)
  types.ts             Lease record + load-state types; canonical column list
  tokens.ts            Cresa design tokens and the region/segment/type color maps
  lib/
    sheets.ts          Sheets API v4 → published-CSV fallback → localStorage cache
    parse.ts           header mapping, Excel-serial/ISO/MTM dates, currency, RFC 4180 CSV
    metrics.ts         every derived number on screen (KPIs, buckets, slices, runway)
    format.ts          $8.04M / 324K / Sep '26 formatting
  hooks/usePortfolioData.ts
  components/          shell, KPI band, four views, map + property detail
  dev/fixture.ts       dev-only sample rows (never used in a deployed build)
sheet-template/        CSV to import into a new Google Sheet
```

**Stack:** React 19 + Vite + TypeScript, `d3-geo` + `topojson-client` + `world-atlas` for the map.
No UI framework — the design system is fully expressed in `src/tokens.ts` and `src/styles.css`.

### Data flow

1. `usePortfolioData` fetches on load: Sheets API v4 when `VITE_SHEETS_API_KEY` is set, otherwise
   the published-CSV endpoint.
2. `parseRows` maps headers (tolerant of case, spacing, and punctuation), normalizes each row, and
   collects per-row warnings instead of throwing — a bad date or a missing coordinate degrades one
   cell, not the page.
3. A successful response is written to `localStorage`. If a later fetch fails, the last-good copy
   renders with an amber "CACHED" chip and the error on hover. With no cache, the page explains
   what to check instead of showing zeros.
4. `buildMetrics` derives everything else. Nothing is pre-aggregated in code.

### Map

Real geometry only: Natural Earth 110m countries (`world-atlas`) via `d3-geo`'s
`geoNaturalEarth1`, Antarctica excluded and the extent cropped to match. One circle per lease at
its `LAT`/`LNG`, radius on a sqrt scale of SF, filled by region color, with a gold ring on active
transactions. Hover for a tooltip, click for the detail panel. Rows without coordinates are
counted everywhere else and reported in the card header.

## Conventions

- **Square corners everywhere** (`border-radius: 0`) and **Arial only** — both are Cresa brand
  rules, not stylistic choices. Gold is for emphasis only; the logo is never recolored or stretched.
- The "expiring soon" window is a setting (`VITE_EXPIRING_MONTHS`, default 12), not a magic number.
  It drives the KPI, the amber dates in three views, and nothing is hard-coded against 2026.
- Year buckets and runway ticks are computed from today's date, so the dashboard ages correctly.

## Tests

```bash
npm test
```

Covers date/currency parsing (Excel serials, ISO, US formats, `MTM`, junk), header mapping,
CSV quoting, and the metrics engine (totals, buckets, slices, region ordering, runway clamping,
attention flags, and the empty-portfolio case).

## Roadmap

Designed for, not yet built: headcount per site (→ cost per seat, SF per person), rent escalations
and an obligation curve, market benchmarking, budget vs actual. The record schema is extensible —
unrecognized sheet columns are preserved on each record rather than dropped, so a `HEADCOUNT`
column can go into the sheet before the UI reads it.
