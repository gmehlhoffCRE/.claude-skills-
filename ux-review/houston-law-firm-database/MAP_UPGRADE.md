# Map styling & markers

The map has **two modes**, chosen automatically by the `GMAPS_MAP_ID` constant near
the top of the script. You don't have to do anything to get the muted, POI-free look
— it works out of the box.

```js
const GMAPS_MAP_ID = 'DEMO_MAP_ID';   // default → in-code styling (mode A)
```

## Mode A — default, works immediately (no Google Cloud setup)

When `GMAPS_MAP_ID` is `'DEMO_MAP_ID'` (or empty), the app styles the base map
**in-code** with the muted, all-POI-off `cresaStyles` array, and uses classic
markers. This renders correctly the moment you open the file with a valid API key —
**nothing to configure**. This is almost certainly what you want.

- Muted, desaturated base; every point of interest hidden.
- Markers keep the size hierarchy (small single dots, larger clusters with a count,
  gold selection).
- Trade-off vs. Mode B: markers are the classic type (no CSS drop-in animation), and
  the client re-styles tiles on zoom, so very fast zooming can feel slightly less
  smooth on big screens.

## Mode B — optional upgrade: Advanced Markers + server-side tiles

`AdvancedMarkerElement` (GPU/DOM markers, animated pins, no zoom lag) **requires a
cloud Map ID**, and a Map ID makes Google ignore in-code styling. So to use Mode B
you recreate the muted/no-POI look as a **cloud style** and attach it to a Map ID.

> ⚠️ **Important — the legacy JSON does not import into the new cloud editor.**
> Google's current "Map styles" editor uses a **new format** (you'll see something
> like `{ "variant": "light" }`, with a *Map features* panel of toggles). Our
> `cresa-map-style.cloud.json` is the **legacy** style-array format — it works great
> for **Mode A (in-code)** but the new cloud editor will not apply it. If you upload
> it there, the map stays on Google's default (bright, POIs showing) — which is the
> preview you saw.

To do Mode B in the new editor:

1. **Google Cloud Console → Google Maps Platform → Map styles → Create style.**
2. In the **Map features** tab, set the map variant to **Light**, then turn **off**
   the POI categories (Business, Attractions, Transit, etc.). Nudge colors toward the
   muted Cresa palette if you like (land `#F3F4F6`, water `#E2E7EC`, roads near-white,
   highways light grey `#EAECF1`). Save.
3. **Map management → Create Map ID** (JavaScript / Raster) and associate the style.
4. Put the Map ID in the code: `const GMAPS_MAP_ID = 'your-id';`
5. Reload. The app auto-switches to Advanced Markers on the cloud-styled base.

`cresa-map-style.cloud.json` is kept as the **reference palette** (and the exact
source for Mode A's in-code style) — use it as the spec while toggling the new editor.

## Recommendation

Stick with **Mode A** unless you specifically want the animated GPU markers and have
a Map ID set up. Mode A already gives you the muted, POI-free premium map with zero
console work — which is exactly what was asked for.

## Marker design (both modes)

Sizing is hierarchical so a multi-firm building always outranks a single firm:

- **Single firm:** small navy dot; selected → gold with a navy index number.
- **Cluster:** larger navy badge with the firm count; **sized by how many firms share
  the building**; selected → gold ring. (Mode B adds a coordinate nub + hover/drop
  animation; Mode A uses the classic circle marker.)
