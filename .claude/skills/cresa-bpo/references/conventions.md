# Cresa BPO conventions

These came out of building the Mogas (14330 E Hardy St, 1601 Peach Leaf St) and 13550 S Gessner Rd BPOs. Follow them
unless the user says otherwise for a specific report.

## Writing style
- No em dashes anywhere (user preference). Use commas, periods, colons or parentheses.
- Use typographic apostrophes (’) in body text; keep feet marks straight (26').
- Plain, confident broker prose. Paraphrase CoStar submarket commentary; never copy it verbatim.
- Address format: street abbreviations in tables and callouts ("14330 E Hardy St"), spelled out in body text
  ("14330 East Hardy Street"). When a DTF or ownership document gives the address, it wins over CoStar/CAD naming.
- Use "\u00b1" for approximate areas in tables and callouts.

## Data rules
- Leave out assessed (HCAD/FBCAD) values. The user asked to drop them.
- Building SF: use what the user designates. Defaults: ownership data (DTF, building sheets) > CoStar > CAD. Flag big
  gaps (for example HCAD 6,250 SF vs DTF 22,450 SF) instead of silently picking one. Exclude parking garages from
  building SF and say so ("excl. ±59,250 SF garage").
- Land area: CoStar acreage unless the user says otherwise; mention extra adjacent parcels owned by the same owner as a
  question, not as fact.
- Covered storage (roofed, not enclosed) is called out separately everywhere it appears: intro, stat label
  ("Enclosed + Covered Area"), Property Summary breakdown, aerial callout, pricing narrative.
- Don't include a land-to-building ratio unless asked; garages and covered areas make it misleading.
- Floodplain: report the FEMA zone and whether the site is in the Special Flood Hazard Area. A 500-year zone is a
  positive point for pricing (no mandatory flood insurance).
- If a fact can't be confirmed, write "TBD" in the table rather than guessing.

## Page content patterns
- **Intro (3 paragraphs):** (1) "At your request, Cresa has prepared a Broker Price Opinion (BPO) for ..." (2) the
  property: SF, acreage, frontage, nearest highways, year built, office/warehouse split, key features (clear height,
  loading, power, cranes, fencing), current use and the vacant/leaseback assumption. (3) Purpose, fee simple, range from
  suggested asking to expected trade, no inspection, data sources, not a certified appraisal.
- **Stat panel:** property type (one word fits best: Warehouse, Manufacturing, Industrial), SF, acres.
- **Property Summary:** about 11 to 13 rows. Typical: Address, Submarket, Parcel #, Land, Building SF, Breakdown,
  Year Built, Clear Height, Loading, Power, Site/Parking, Occupancy at Sale, Floodplain. Multi-parcel sites get one row
  per parcel ("±58,727 SF on 1.73 AC\nHCAD 0041760000227 | 14330 E Hardy St"). Parcel map shows outlines with no
  numbers (the user numbers them in InDesign if needed).
- **Location (2 paragraphs):** distances to the nearest freeways, Beltway 8, airport and downtown, measured on the map
  (not guessed), then a sentence on access/connectivity plus the highest CoStar traffic count near the site.
- **Demographics:** 11 standard rows (see template). Prefer the detailed CoStar Demographics tab over the property
  summary card when they differ. Summary paragraph: residents and daytime employees within 5 miles, annual growth, then
  one standout (income, goods-producing share, or traffic count).
- **Aerial callouts:** title = address or parcel label; 2 to 3 short lines (SF with year, clear/loading, acres).
- **Building Summary (optional):** used when ownership supplies per-building or per-parcel specs. Include a totals row
  and a Site Improvements table (Yard/Paving, Fencing/Security, Power, Rail, Water/Sewer, Zoning).

## Comps
- Order by close date, most recent first. Map markers, Map Key and matrix share that numbering.
- Up to 5 per matrix page; add pages as needed. Fewer than 5 comps get wider columns.
- Fields come from what the user's sources provide. Drop rows that are empty for every comp (for example Price/AC when
  no acreage was given) and swap in rows that have data (Year Built, Notes, Sale Type, Clear Height).
- Missing values show "N/A". A price not given shows "Not disclosed"; offer an estimate from $/SF but don't insert it unasked.
- Flag duplicates (same address, near-identical dates and prices) and ask before dropping them.
- Broker credits: point out when a broker on the BPO appears as a party on a comp before it goes to a client.

## Pricing
- Show Suggested Asking and Expected Trade as $/SF (two decimals, computed from the rounded total) and total.
- When the user gives a $/SF spread (e.g. "$90 to $100"), map the top to asking and the bottom to expected trade unless
  told otherwise. When they give a value range plus an underwriting value, use the top of the range as asking and the
  underwriting value as expected trade, and say so.
- When asked to recommend pricing, reason from the closest comps (size, age, clear height, location, user vs investment
  sale), adjust for land/yard, covered vs enclosed area, office share, loading and garages, and cross-check with a simple
  rent x cap rate lease-up estimate. State which assumptions are yours.
- If the SF basis changes after pricing is set, recompute $/SF and tell the user how the per-SF numbers moved.
- Narrative (2 paragraphs): market and comps context, then why the Subject sits where it does in the range, ending with
  the asking and expected trade figures.

## Maps
- Google Static Maps via the user's key: hybrid for the parcel map, satellite for the aerial, roadmap elsewhere.
- Google logo and attribution must stay visible (their terms). They are already reduced to the minimum legible size;
  if asked to remove them, explain why not and offer to make them less noticeable or switch roadmap pages to
  OpenStreetMap with a page credit.
- Location page: small map is citywide; large map zoomed in on the site.
- Comps map must show every comp with room around the outer markers and keep the Map Key clear of markers. Re-run
  `--maps comps` with `map_options` tweaks if not.

## Bank branch and retail-use sites
- Location write-ups focus on visibility and on access for clients and employees (frontage, signalized corners, turn
  lanes, freeway exits, parking at the door, surrounding household and business base), not freight or distribution.
- Measure distances with Google (Distance Matrix or straight-line to verified interchange coordinates). Google's geocodes
  for freeway "A & B" intersections are often wrong; sanity-check them before quoting.
- Demographic rows for these sites: Population (2025), Projected Population (2030), Population Growth (2025-2030, total %
  computed from the two counts), Annual Growth (2025-2030), Households, Median Age, Median and Average Household Income,
  Median Home Value, Daytime Employees, Total Businesses, Consumer Spending (Annual). The summary leads with 5-mile
  residents and employees, then the 5-year growth (% and new residents), then one standout.
- When the client's facility inventory and CoStar disagree on SF, use the inventory figure only unless told otherwise;
  don't print the CoStar figure beside it. List the conflict in the reply instead.
- List the banking features the inventory gives (drive-thru lanes, ATM/ITM, safe deposit, after-hours depository).

## Leased sites
- Value the lease: market rent opinion (asking vs. expected achievable rent per RSF per year) with lease comps.
- Lease Summary and Cash Flow Pro Forma pages come from the lease workbook; never fill lease terms that aren't in a lease
  abstract or client data. CoStar lease expirations can be shown as "(CoStar)" until confirmed.
- Contract vs. market: within 2.5% reads "in line with market"; outside that, state the % above or below.
