---
name: cresa-bpo
description: Build Cresa Houston Broker Price Opinion (BPO) reports as editable InDesign IDML packages with Google Maps imagery, parcel outlines, comps, demographics and pricing. Use this skill whenever the user asks to create, start, update or revise a BPO or broker price opinion, mentions a property they need valued or priced for a client, uploads CoStar property, demographics or comp screenshots for a BPO, or asks for comps maps, aerials or property summary pages in the Cresa BPO format, even if they don't say "BPO" explicitly.
---

# Cresa BPO builder

Produces a 10+ page landscape (11 x 8.5) BPO in Cresa's template: cover, intro with stat panel, Property Summary with
parcel map, Location, Demographics with 1/3/5 mile rings, full-page Overhead Aerial with callouts (dropped for leased sites), optional Building
Summary, comps map, comps matrix (5 per page), optional Lease Summary and Cash Flow Pro Forma (leased sites), Market Value, and the "Beyond Space" back page. Output is a zip with the
`.idml`, a `Links/` folder of 300 dpi images, and a preview PDF.

Everything content-related lives in one `property.json`. The scripts handle maps, layout and packaging.

## Workflow

1. **Intake.** Read what the user sent (CoStar screenshots, DTF spreadsheets, HCAD/FBCAD tables, comp sheets, photos).
   Then ask, in one message, only for what's missing from this checklist:
   - Google Maps API key (Static Maps + Geocoding). Ask every time; never write it into files or memory.
   - Vacant delivery or leaseback / leased investment? (Mogas reports assumed vacant.)
   - Owned or leased by the client? Leased sites get a market rent opinion plus the lease pages (see "Leased sites").
   - Brokers for the back page (name, title, phone, email).
   - Which source governs land and building SF when CoStar, the appraisal district and ownership disagree.
   - Comps, the full CoStar Demographics tab (1/3/5 mile), and any pricing guidance.
   Don't block on missing items: build with placeholders and list what's still open.

2. **Locate and outline the site.** Work in `/home/claude/bpo_<slug>/` (the container resets between sessions, so keep
   all inputs there and copy the skill's scripts path from wherever it's installed).
   ```bash
   S=<skill path>/scripts
   python $S/parcels.py geocode "13550 S Gessner Rd, Missouri City, TX 77489"
   python $S/parcels.py hcad 0041760000227 1310110010001 --out parcels.geojson      # Harris County by account #
   python $S/parcels.py near <lat> <lon> --county fortbend --dist 80                  # list nearby Fort Bend parcels
   python $S/parcels.py fbcad 3518-01-000-0010-907 --out parcels.geojson             # Fort Bend by property #
   ```
   Show the user owner/acreage for the parcels you picked. Flag any parcel with a different owner or any acreage that
   disagrees with CoStar; let the user decide what's in the sale. Census geocoding misses frontage-road addresses like
   "W Sam Houston Pkwy N"; `parcels.py geocode` falls back to Google when `GKEY` is set. FBCAD's public GIS service may
   require a token; when parcel queries fail, omit `parcels_geojson` and the maps frame a pin with a buffer
   (`map_options.pin_radius_m`, default 70 m).

3. **Write `property.json`.** Copy `templates/property_template.json` and fill it. Read `references/conventions.md`
   before writing any narrative, table rows or pricing; it holds the house rules and wording patterns the user approved.
   Geocode every comp and store `lat`/`lon`. Put comp photos in the work folder and reference them with `photo_src`.
   Property photos go in `cover_photo` and `intro_photo` (`{"src": "photos/x.jpg", "focus": [0.5, 0.4]}`); the build
   crops them to the frame and warns when a source is under 300 dpi at placed size.

4. **Build.**
   ```bash
   GKEY=<key> python $S/build.py property.json --work /home/claude/bpo_<slug>
   ```
   Use `--maps none` for text-only edits, or `--maps comps` (or `site,aerial`) to redraw specific maps. The script prints
   any `OVERSET` or `CELL OVERFLOW` warnings from the preview pass; fix those by trimming text before delivering.

5. **Check, then deliver.** Render the preview to PNG (`pdftoppm -r 40`) and look at every page: map framing, markers
   clear of the Map Key, callouts not covering the parcel or title, no clipped text. Copy the zip and preview PDF to
   `/mnt/user-data/outputs/` and present them. In the reply, list what changed and every open question or data conflict.

## Leased sites (market rent opinion)

For a site the client leases, the report values the lease rather than the fee simple interest:

1. In `property.json` set `pricing.mode = "lease"` (value table becomes Rent/SF/Yr, SF, Annual Rent), `comps_title =
   "Recent Lease Comps"`, lease `comp_fields`, and a lease `disclaimer` (examples in the template `_notes`).
2. Build the lease workbook: copy `templates/lease_sites_template.json`, list one site per leased location, then
   ```bash
   python $S/lease_workbook.py lease_sites.json Lease_Pro_Forma.xlsx
   python <xlsx skill>/scripts/recalc.py Lease_Pro_Forma.xlsx 60
   ```
   Each tab has yellow input cells (commencement, expiration, current base rent, escalation, expense pass-through, free
   rent, options, Cresa market rent opinion) and calculates the Lease Summary and a lease-year Cash Flow Pro Forma.
   Escalations hit on each anniversary of the original commencement. Hand the workbook to the user to fill from the
   lease abstracts; never invent lease terms.
3. Push the workbook into the reports (adds Lease Summary and Cash Flow Pro Forma pages before Market Value, drops the
   Overhead Aerial page via `skip_aerial`):
   ```bash
   python $S/lease_to_json.py Lease_Pro_Forma.xlsx lease_map.json   # {"<work>/property.json": "<tab name>", ...}
   ```
   Empty inputs render as TBD, so the pages can ship as placeholders. Re-run after the user fills the workbook, then
   rebuild with `--maps none`.

For multi-tenant buildings, describe the building or center first, then the client's specific premises (suite, SF,
banking or use features). Use the stat panel labels (`stat_labels`) to say "Client Premises" and "Center Land Area".

## Revisions

Edit `property.json` and rebuild. When only one image changes (for example the comps map), also hand the user that PNG on
its own so they can swap it into their working InDesign file instead of reopening a new IDML, which would discard their
manual edits. Mention that option whenever they've likely been editing in InDesign.

## Files

- `scripts/build.py`: orchestrates maps, photo crops, IDML, preview PDF and zip.
- `scripts/bpo_spec.py`: page layout (positions, styles, colors). Change layout here, not per property.
- `scripts/gmaps.py`: Google Static Maps tiles, stitching, brand markers, rings, parcel overlays, attribution.
- `scripts/idml.py`, `scripts/preview.py`: IDML writer and ReportLab preview renderer for the same layout.
- `scripts/parcels.py`: HCAD / FBCAD parcel queries and geocoding.
- `scripts/lease_workbook.py`, `scripts/lease_to_json.py`: lease snapshot / pro forma workbook and its hand-off into the
  Lease Summary and Cash Flow Pro Forma pages.
- `templates/lease_sites_template.json`: input for `lease_workbook.py`.
- `templates/property_template.json`: every field the layout reads, with examples.
- `references/conventions.md`: house rules, narrative patterns, pricing method, map rules.
- `assets/cresa_logo.png`: logo used on every page.
