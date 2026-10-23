# Cresa Healthcare Practice Group: One-Pager and Bifold

Editable InDesign files (IDML) plus PDF proofs.

| Piece | File | Format |
|---|---|---|
| One-pager, front and back | `Cresa_Healthcare_OnePager/Cresa_Healthcare_OnePager.idml` | Letter, 2 pages |
| Bifold brochure | `Cresa_Healthcare_Bifold/Cresa_Healthcare_Bifold.idml` | Letter, 4 pages (cover / inside spread / back); prints on 11×17 folded to letter |
| One-pager, Houston edition | `Cresa_Healthcare_OnePager_Houston/Cresa_Healthcare_OnePager_Houston.idml` | Letter, 2 pages |
| Bifold, Houston edition | `Cresa_Healthcare_Bifold_Houston/Cresa_Healthcare_Bifold_Houston.idml` | Letter, 4 pages |

**Houston editions** drop the 2024 national stats. The one-pager replaces them with "Questions we help you answer" (three client questions with how the analytics answer each); and "Houston" appears in the practice labels, cover, hero copy and footers. The case studies and client logos are national and are unchanged.

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
