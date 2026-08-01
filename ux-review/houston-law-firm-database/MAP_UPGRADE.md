# Map upgrade — AdvancedMarkerElement + cloud Map ID

This build migrates the map from the deprecated `google.maps.Marker` to
**`AdvancedMarkerElement`** (GPU-accelerated, DOM-based markers). The pins and
clusters are now real HTML/CSS elements, so they animate (drop-in, hover-scale,
selection pop) and render far more smoothly.

## Why a Map ID is required (and why it's a good thing)

`AdvancedMarkerElement` **only works on a map created with a cloud `mapId`.** The
code already passes one:

```js
const GMAPS_MAP_ID = 'DEMO_MAP_ID';   // ← replace with your own (see below)
```

`DEMO_MAP_ID` makes everything work immediately, but it renders Google's **default**
base map — you lose the Cresa styling (warm off-white land, navy highways, muted
parks). To get the Cresa look back, the map style has to move from the code into a
**cloud style** attached to your own Map ID.

That migration is also what **fixes the zoom lag** noted in the README: with a cloud
Map ID, tiles are styled **server-side** instead of re-running 26 style rules per
tile in the browser on every zoom.

## One-time setup (~10 minutes)

1. Go to **Google Cloud Console → Google Maps Platform** (make sure the correct
   project is selected — the one whose API key is in the file).
2. **Map styles** → **Create map style** → **Import JSON** → paste the full contents
   of **`cresa-map-style.cloud.json`** (shipped next to the HTML file). Choose the
   **Raster** map type, name it `Cresa Houston`, and **Save**. (POIs are already
   turned off inside the JSON — nothing else to toggle.)
3. **Map management** → **Create Map ID**:
   - Map type: **JavaScript**
   - Rendering: **Raster**
   - **Associate** it with the `Cresa Houston` style from step 2.
4. Copy the new Map ID (looks like `a1b2c3d4e5f6g7h8`).
5. In the HTML, replace the placeholder near the top of the script:
   ```js
   const GMAPS_MAP_ID = 'YOUR_MAP_ID_HERE';   // was 'DEMO_MAP_ID'
   ```
6. Reload. The muted, POI-free Cresa base returns, tiles render pre-styled (no zoom
   lag), and the Advanced Markers sit on top.

> If you later tweak the palette, edit the style in the console (or re-import an
> updated `cresa-map-style.cloud.json`) — no code change needed, the Map ID stays
> the same.

> Tip: keep your API key restricted to your domain(s) (HTTP referrers) in the
> console — the same key is already in the file.

## What changed in the code

- Maps loader now requests the marker library: `&libraries=marker&v=weekly`.
- `initMap` creates the map with `mapId: GMAPS_MAP_ID`; the client-side
  `StyledMapType` is removed (ignored when a Map ID is set — kept only as the source
  for the cloud JSON).
- The MAP / HYBRID toggle switches between `roadmap` (your cloud style) and `hybrid`.
- Markers are built as DOM content (`makeMarkerEl`) and their live state
  (selection number, cluster count + size tier, hover/active, z-order) is painted by
  `paintMarker` — replacing the old `setIcon`/`setLabel` calls.
- The dashboard peer mini-map was migrated too.
- A capability guard means that if the marker library ever fails to load, the app
  logs a clear message instead of throwing (the map just shows no pins).

## Marker design (upgraded)

Sizing is deliberately hierarchical — a multi-firm building always reads as more
important than a single firm:

- **Single firm:** a compact navy **dot** (13px) centered on the coordinate.
  Selected → 22px gold dot with a navy index number. Hover/active → scales.
- **Cluster:** navy circular badge with a downward nub pointing at the exact
  coordinate, white firm count, **sized by how many firms share the building**
  (34 / 40 / 48 px). Selected → gold ring (count stays legible). Hover/active → scales.
  Even a selected, hovered single dot stays clearly smaller than the smallest cluster.
- **Drop-in entrance** when markers appear; all motion respects
  `prefers-reduced-motion`.

## Base map style (muted, POI-free)

`cresa-map-style.cloud.json` is a **muted, low-contrast** palette with **all points
of interest hidden**: desaturated land and water, soft-grey roads, highways in light
grey rather than navy, and every POI category (business, attraction, medical, school,
transit…) turned off — only a faint, unlabeled park fill remains for orientation. The
navy highways and bright POIs previously competed with the navy markers; muting the
map and clearing POIs lets the pins and clusters carry all the visual weight.

Until this style is attached to a real Map ID, `DEMO_MAP_ID` shows Google's **default**
base map (bright, POIs on) — that is expected, not a bug.

## Verifying

Open the app with a valid API key + Map ID and confirm: pins drop in, hovering a
firm card rings its pin, selecting adds the gold/number treatment, multi-firm
buildings show a sized cluster that opens the firm popover, and MAP/HYBRID toggles
cleanly. (This can only be checked with live Google Maps — it can't render offline.)
