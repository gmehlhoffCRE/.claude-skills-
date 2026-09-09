# Setup — connect the dashboard to your Google Sheet

The dashboard has **no lease data in its code**. Every KPI, chart, map dot, and table row is
computed from rows fetched out of one Google Sheet at load time. Update the sheet, reload the
page, and the dashboard reflects it — no deploy required.

Budget about 15 minutes for the first run-through.

---

## 1 · Create the sheet

1. Open <https://sheets.google.com> and create a blank spreadsheet.
   Name it something like **Rimkus Real Estate Portfolio**.
2. Rename the first tab to **`Portfolio`** (bottom-left tab → double-click).
   If you use a different name, set `VITE_SHEET_NAME` to match.
3. Seed it with the template: **File → Import → Upload** →
   [`sheet-template/portfolio-template.csv`](sheet-template/portfolio-template.csv) →
   *Replace current sheet* → *Import data*.
   That gives you the header row plus the 60 sample records to overwrite with live data.

### Column schema

Row 1 must be the header row, spelled as below (case and spacing are forgiving — the parser
normalizes them — but the wording must match):

| Column | Type | Notes |
|---|---|---|
| `LEASE TYPE` | text | Direct Lease / Sublease / Exec Suite |
| `REGION` | text | West / Southeast / South Central / Northeast / Canada / International |
| `TRANSACTION STATUS` | text | `Active` = open transaction (drives the Pipeline view and the gold map ring); anything else is treated as inactive |
| `OPERATING SEGMENT` | text | Forensics, BES, Life Sciences, Corporate, Corp/Forensics, BES/Forensics, EMEA, APAC |
| `LEASE CITY` | text | |
| `ST` | text | state / province / country code |
| `STREET ADDRESS` | text | |
| `PROPERTY TYPE` | text | Flex / Office / Warehouse / Exec Suite |
| `SF` | number | rentable square feet |
| `LEASE EXP` | date or `MTM` | Excel serial, ISO (`2029-01-31`), `1/31/2029`, `Jan 31, 2029`, or `MTM` for month-to-month |
| `ANNUAL GROSS RENT ($US)` | number | `$` and thousands separators are fine |
| `CRESA NOTES` | text | free text; drives Needs Attention, the Pipeline "next step" column, and the runway colors |
| `LAT` | number | decimal degrees, e.g. `29.78` |
| `LNG` | number | decimal degrees, e.g. `-95.62` |

Notes on behavior:

- **Region, segment, and property-type colors** are keyed off the exact values above. A value
  outside the list still renders — it just falls back to a neutral gray.
- **`CRESA NOTES` keywords matter.** A note containing "clos" (and not "subleas") flags the lease
  as *closing at expiration* — red on the runway, red chip in Needs Attention. A note containing
  "subleas" flags it as a sublease (gold chip).
- **`LAT`/`LNG` are the only added columns** versus the client's original workbook. A row without
  them is included in every metric but omitted from the map, and the map card header says how many.
  Geocode once and paste the values in — the app never geocodes at load time.
- **Extra columns are preserved**, not dropped, so you can add `HEADCOUNT` (or anything else on the
  roadmap) to the sheet before the UI supports it.

---

## 2 · Choose an access method

### Option A — Sheets API v4 (recommended)

Typed values, no publishing, and the sheet stays out of search results.

1. Go to <https://console.cloud.google.com/> → create (or pick) a project.
2. **APIs & Services → Library** → search "Google Sheets API" → **Enable**.
3. **APIs & Services → Credentials → Create credentials → API key**.
4. Click the new key → **Edit API key**:
   - *Application restrictions*: **Websites**, and add the origins that will serve the dashboard
     (e.g. `https://portfolio.yourdomain.com/*`, plus `http://localhost:5173/*` for local dev).
   - *API restrictions*: **Restrict key** → select **Google Sheets API** only.
5. Back in the sheet: **Share → General access → Anyone with the link → Viewer**.
   An API key can only read a link-shared sheet.
6. Copy the sheet ID out of its URL:
   `https://docs.google.com/spreadsheets/d/`**`1AbC…xyz`**`/edit#gid=0`

> **Sensitive portfolio?** "Anyone with the link" means anyone holding the link can read the sheet,
> and the API key ships in the browser bundle. If that is not acceptable, keep the sheet private
> and put a small server-side proxy in front of it using a **service account** (share the sheet with
> the service-account email as Viewer, have the proxy call `spreadsheets.values.get`, and point the
> app at the proxy). The client code needs no change beyond the URL.

### Option B — Published CSV (no key)

Fastest to stand up; the sheet becomes publicly readable at a Google URL.

1. **File → Share → Publish to web** → *Entire document* or the `Portfolio` sheet → **CSV** →
   **Publish**.
2. Leave `VITE_SHEETS_API_KEY` blank. The app falls back to
   `https://docs.google.com/spreadsheets/d/<id>/gviz/tq?tqx=out:csv&sheet=Portfolio`.
3. If your tab is not the first one, also set `VITE_SHEET_GID` to the `gid=` value in the sheet URL.

Publishing lags edits by up to ~5 minutes; the API reflects them immediately.

---

## 3 · Configure and run

```bash
cd portfolio-dashboard
npm install
cp .env.example .env.local        # then fill in VITE_SHEET_ID (and the API key, if using one)
npm run dev                       # http://localhost:5173
```

Working offline or before the sheet exists? Run against the bundled sample fixture:

```bash
VITE_USE_FIXTURE=true npm run dev
```

The fixture is dev-only seed data and is never used when `VITE_USE_FIXTURE` is unset.

### Environment variables

| Variable | Required | Default | Purpose |
|---|---|---|---|
| `VITE_SHEET_ID` | yes | — | Spreadsheet ID from the sheet URL |
| `VITE_SHEET_NAME` | no | `Portfolio` | Tab name |
| `VITE_SHEETS_API_KEY` | no | — | Enables the Sheets API path; blank falls back to published CSV |
| `VITE_SHEET_GID` | no | — | Tab gid, for the CSV fallback on non-first tabs |
| `VITE_EXPIRING_MONTHS` | no | `12` | "Expiring soon" window — drives the KPI and every amber date |
| `VITE_RUNWAY_MONTHS` | no | `66` | Span of the expiration runway timeline |
| `VITE_SOURCE_LABEL` | no | Cresa/Rimkus line | Footer provenance text |
| `VITE_USE_FIXTURE` | no | `false` | Dev-only: use the bundled sample rows |

---

## 4 · Publish

```bash
npm run build      # outputs dist/
npm run preview    # verify the production build locally
```

`dist/` is static — host it anywhere that serves files:

- **Netlify / Vercel / Cloudflare Pages** — point at this folder, build `npm run build`, publish
  `dist`, and set the `VITE_*` variables in the host's environment settings (they are read at
  build time, so redeploy after changing one).
- **Google Cloud Storage / S3 + CDN** — upload `dist/` and serve `index.html` as the index doc.
- **Internal server** — copy `dist/` behind whatever auth your intranet already uses. This is the
  simplest way to keep the dashboard itself private.

Whichever host you pick, add its origin to the API key's website restrictions (Option A, step 4).

---

## 5 · Verify

Open the dashboard and check the header chip:

| Chip | Meaning |
|---|---|
| green · `LIVE · 60 LEASES · $8.04M AGR` | Sheet answered; these numbers came from your rows |
| amber · `CACHED 3:42 PM · …` | Fetch failed; showing the last good copy from this browser. Hover for the error |
| red · `NO DATA · RETRY` | Fetch failed with no cached copy — the panel on screen lists what to check |

Hover the chip for the fetch time, the transport used, and any per-row warnings (unreadable
expiration dates, missing coordinates). Click it to re-fetch without reloading.

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `403 PERMISSION_DENIED` | Sheet is not link-shared, or the API key's website restriction excludes this origin |
| `400 API key not valid` | Key restricted to the wrong API — allow Google Sheets API |
| "Published CSV returned HTML" | The sheet is not published to the web (Option B, step 1) |
| `Sheets API 404` | Wrong `VITE_SHEET_ID`, or `VITE_SHEET_NAME` does not match the tab |
| Some sites missing from the map | Those rows have blank `LAT`/`LNG` — the map card header counts them |
| An expiration shows `MTM` unexpectedly | The cell is blank or unparseable; hover the status chip for the row number |
| Numbers look stale | Published-CSV lag (~5 min) — or you are on cached data; check the chip color |
