# Prompt for Claude Code

Paste this into Claude Code from the folder where you want the app built (with this handoff folder inside it):

---

Build a production web app from the design handoff in `design_handoff_portfolio_dashboard/`. Read `README.md` in that folder first — it is the full spec — then study the two HTML prototypes (`Rimkus Portfolio Dashboard.dc.html`, `portfolio-map.html`) as high-fidelity visual references and recreate them faithfully (Cresa brand: Arial, Midnight #001E5A, Goldenrod #FFB600 accents, square corners).

Key requirements:

1. **Google Sheets is the single source of truth.** No lease/location data may be hard-coded anywhere. On load, fetch all rows from a Google Sheet (Sheets API v4 preferred; published-CSV fallback acceptable) using the column schema in the README, compute every KPI, chart, map dot, and table row from those rows, and show a live/stale data-source chip in the header. Use `portfolio-data.sample.js` only to seed a dev fixture and a template Sheet I can copy. Make the spreadsheet ID/API key configuration via env vars, and include a `SETUP.md` telling me exactly how to create/share the sheet and publish the app.
2. Four views: Overview (world map with clickable property-detail dots + charts), Expirations (runway/Gantt + by-year rail), Pipeline (active transactions), All Sites (sortable/searchable/filterable full table). All specified precisely in the README.
3. The map must use real geometry (d3-geo + world-atlas TopoJSON, geoNaturalEarth1) — never hand-drawn shapes. Lat/lng come from sheet columns.
4. Handle loading, fetch-failure (cached last-good data + amber indicator), empty notes, "MTM" expirations, and Excel-serial or formatted dates defensively.
5. Choose a clean modern stack (React + Vite + TypeScript suggested), no heavy UI framework — the design system is fully specified in tokens.

Work through the README section by section and verify each view against the prototypes before calling it done.
