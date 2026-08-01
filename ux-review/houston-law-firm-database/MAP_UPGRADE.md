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

1. Go to **Google Cloud Console → Google Maps Platform**.
2. **Map styles** → **Create style** → choose *"Import JSON"* and paste the contents
   of **`cresa-map-style.cloud.json`** (shipped next to the HTML file). Save it as
   `Cresa Houston`. Pick the **Raster** map type (matches the current base map).
3. **Map management** → **Create Map ID**:
   - Type: **JavaScript**
   - Map type: **Raster**
   - Associate it with the **Cresa Houston** style you just created.
4. Copy the new Map ID (looks like `a1b2c3d4e5f6g7h8`).
5. In the HTML, set:
   ```js
   const GMAPS_MAP_ID = 'YOUR_MAP_ID_HERE';
   ```
6. Reload. The Cresa base map returns, tiles render pre-styled (no zoom lag), and
   the Advanced Markers sit on top.

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

- **Single firm:** navy teardrop pin, white center dot. Selected → gold pin with a
  navy index number. Hover/active → lifts and scales.
- **Cluster:** navy circular badge with a downward nub pointing at the exact
  coordinate, white firm count, **sized by how many firms share the building**
  (30 / 36 / 44 px). Selected → gold ring (count stays legible). Hover/active → scales.
- **Drop-in entrance** when markers appear; all motion respects
  `prefers-reduced-motion`.

## Verifying

Open the app with a valid API key + Map ID and confirm: pins drop in, hovering a
firm card rings its pin, selecting adds the gold/number treatment, multi-firm
buildings show a sized cluster that opens the firm popover, and MAP/HYBRID toggles
cleanly. (This can only be checked with live Google Maps — it can't render offline.)
