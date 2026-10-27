# Cresa Healthcare Practice Group: One-Pager and Bifold

Editable InDesign files (IDML) plus PDF proofs.

| Piece | File | Format |
|---|---|---|
| One-pager, front and back | `Cresa_Healthcare_OnePager/Cresa_Healthcare_OnePager.idml` | Letter, 2 pages |
| Bifold brochure | `Cresa_Healthcare_Bifold/Cresa_Healthcare_Bifold.idml` | Letter, 4 pages (cover / inside spread / back); prints on 11×17 folded to letter |
| One-pager, Houston edition | `Cresa_Healthcare_OnePager_Houston/Cresa_Healthcare_OnePager_Houston.idml` | Letter, 2 pages |
| Bifold, Houston edition | `Cresa_Healthcare_Bifold_Houston/Cresa_Healthcare_Bifold_Houston.idml` | Letter, 4 pages |
| Road Atlas trifold self-mailer | `Cresa_Healthcare_RoadAtlas_Trifold/Cresa_Healthcare_RoadAtlas_Trifold.idml` | Legal 14×8.5", letter fold; page 1 = outside, page 2 = inside |
| Business cards (Doug McNee, Jason Herbrich) | `Cresa_BusinessCard_<Name>/…idml` | 3.5×2", page 1 = front, page 2 = back |
| Business card alternate back (road atlas) | `Cresa_BusinessCard_AltBack_RoadAtlas/…idml` | 3.5×2", 1 page |

**Houston editions** drop the 2024 national stats. The one-pager replaces them with "Questions we help you answer" (three client questions with how the analytics answer each). The Houston bifold uses the same integrated-services callout as the national bifold. "Houston" appears in the practice labels, cover, hero copy and footers. The case studies and client logos are national and are unchanged.

## Shared style system (from the edited bifold)

All pieces follow the bifold as edited in InDesign. **That InDesign file is the master for the bifold**; the bifold IDML in this folder predates those edits.

- **Practice label:** "HEALTHCARE PRACTICE GROUP" top right, Bold caps, letter-spaced, Bright Blue.
- **Headlines:** two weights (Light, then Medium). Section headings are Medium, title case: Who We Serve, What We Analyze, What We Deliver, What You Gain, Our Process.
- **Navy callouts:** gold left bar, gold Bold caps kicker, white text and white dot bullets. Gold dot bullets on white.
- **Copy:** "What We Deliver" items are Opportunity Scorecards, Analytics/KPI Workbooks, Drive-Time Access Maps, Site Ranking Matrices and Board-Ready Executive Decks. The service lines include Project & Development Services. "What You Gain" wording matches the bifold.
- **Tagline:** "The right diagnosis for your next location." Pair it with the headline "A second opinion you can really trust." Cresa's corporate "Think beyond space." stays in footers.
- **Road-atlas pieces only:** the condensed highway lettering and shield badge.

## Business cards

- **Front:** white, with logo, practice label, name and title, gold rule, mobile, email, cresa.com, office address (placeholder) and a gold edge accent.
- **Back:** navy callout with "A second opinion you can really trust.", the tagline "The right diagnosis for your next location." and a QR frame (URL TBD).
- **Alternate back:** road-atlas shield ("Where will you grow next?") with "The right diagnosis for your next location."
- Check with Cresa marketing whether practice-group cards may vary from the corporate card template.
- **Concept options** (in `BusinessCard_Concepts/`, shown with Doug McNee's details):
  - **C, Bold navy:** navy front with white and gold type; white back with a gold edge bar and a large headline.
  - **D, Vertical:** 2×3.5" portrait, with a gold side bar on the front and a stacked headline and QR on a navy back.
  - **E, Contour:** subtle map contour lines with a gold location pin; the navy back leads with the diagnosis tagline.

## Road Atlas trifold notes

- **Panels:** outside = fold-in flap (What We Do, What You Gain, Service Lines) | mailer back | cover; inside = map spread (two panels) with What We Deliver underneath | case studies, no-conflicts and client logos. The fold-in flap is 4.625", the others 4.6875". Fold lines are drawn on the non-printing layer.
- **Personalization:** `[Company Name]` appears on the cover badge, mailer teaser and map title. The map pins, callout tags and legend are **sample data**. Move or duplicate pins to show each prospect's real footprint.
- **The map** is built from native, editable shapes: states, interstates, shields, labels and pins, from U.S. Census-derived state boundaries (us-atlas, public domain).
- **Mailing:** the address panel is rotated so the address reads along the 8.5" length. Before printing, confirm with your mail house: postage indicia/permit, return address (placeholder), tab or wafer-seal placement, and the barcode clear zone. Folded size is about 4.69" × 8.5", which qualifies as a USPS letter-size mailpiece.
- **Fonts:** condensed headlines use Helvetica Neue LT Pro 67/77/87 Condensed.

## Opening the files

1. Open the `.idml` in InDesign (File > Open). Save as `.indd`.
2. **Fonts:** Helvetica Neue LT Pro (45 Light, 55 Roman, 65 Medium, 75 Bold) must be installed.
3. **Links:** logos are linked from the `Links` folder next to each file. If InDesign reports missing links, open the Links panel, select all, choose **Relink to Folder** and point it at that `Links` folder.
4. **Placeholders:** grey striped frames are empty graphics frames for photos, headshots and the QR code. Select the frame, then File > Place. Their labels sit on the **Placeholder Labels (non-printing)** layer. Delete or hide that layer before final output.

## Document setup

- Bleed is 0.125" on all sides. Facing pages. Process CMYK swatches: Midnight, Goldenrod, Dark Gray, Light Gray, Stadium Blue, Bright Blue, Warm Orange.
- Everything is styled with named paragraph and character styles (Hero, H2, Body, Bullet, Stat Number, etc.). Edit the style, not the text, to restyle globally.
- Icons are native InDesign shapes, so they are editable vectors.
- **Bifold imposition:** the outside sheet is page 4 (back) + page 1 (cover); the inside sheet is pages 2–3. See `proofs/Cresa_Healthcare_Bifold_Proof_11x17_Imposed.pdf`. Export print files from InDesign with PDF/X-4, bleed and crop marks on. For digital, export Interactive or Print PDF with "Spreads" checked so the inside reads as one 17×11 page.

## Still needed before release

- **Photography:** one-pager front hero (vertical clinician and patient), one-pager back image (sample analytics output such as a market heat map or drive-time map), bifold cover (full bleed, calm lower-left area for the title block).
- **Headshots:** Doug McNee and Jason Herbrich (square crop). Frames are labeled.
- **QR code:** landing page URL for the "complimentary Healthcare Market Screen" call to action. Confirm the offer is approved; otherwise change the CTA to "Schedule a strategy call."
- **Client logos:** cropped at 600 dpi from the 2025 Practice Group Overview. Replace with original vector files before print if available. Aliera Healthcare was intentionally left off the logo wall.
- **Stats** are 2024 figures. Update when 2025 numbers are available.

## Proofs

The PDFs in `proofs/` are layout proofs rendered outside InDesign with a substitute font, so line breaks will shift slightly in InDesign. Copy fit was checked with a wider font than Helvetica Neue, so text should fit with room to spare.

## Regenerating

`source/` holds the generator: `layouts.py` has all copy and positions; `idmlkit.py` writes the IDML and HTML proofs. Run `python3 build.py <outdir>`, then `node render.js <outdir> <name>_proof` with Playwright for PDFs. Requires Pillow and lxml.
