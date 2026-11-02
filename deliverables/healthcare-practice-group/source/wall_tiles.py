"""Copy the trifold's framed logo tiles into the bifold back page (2 rows x 6), replacing the old logo wall.
Usage: wall_tiles.py <unpacked bifold dir> <unpacked trifold dir> <out.idml>"""
import copy
import os
import sys
import zipfile

from lxml import etree

BIF, TRI, OUT = sys.argv[1:4]
PX, PY = -612.0, -396.0
SP = os.path.join(BIF, "Spreads", "Spread_u5c5.xml")
tree = etree.parse(SP)
spread = tree.getroot().find("Spread")
OLD_WALL = "u7b3 u7b7 u7bc u7c1 u7c6 u7cb u7cf u7d5 u7da u7df u7e3 u7e7".split()
for el in list(spread):
    if el.get("Self") in OLD_WALL:
        spread.remove(el)

tri = etree.parse(os.path.join(TRI, "Spreads", "Spread_u46e.xml")).getroot().find("Spread")
SRC = {el.get("Self"): el for el in tri.iter("Rectangle")}
# DaVita is a case study on the bifold, so Dispatch Health takes its tile
ORDER = [("u1e1a", "u1c98"), ("u1e1b", None), ("u1e1c", None), ("u1e1d", None), ("u1e1e", None), ("u1e1f", None),
         ("u1e20", None), ("u1e21", None), ("u1e22", None), ("u1e23", None), ("u1e24", None), ("u1e25", None)]
TW, TH, GAP = 82.0, 40.0, (540 - 6 * 82.0) / 5
ROWS = [361.0, 405.0]
nid = [0x9000]


def new_id():
    nid[0] += 1
    return f"u{nid[0]:x}"


def bounds(el):
    pts = [tuple(map(float, p.get("Anchor").split())) for p in el.find("Properties/PathGeometry").iter("PathPointType")]
    m = [float(v) for v in el.get("ItemTransform").split()]
    xs = [m[0] * x + m[2] * y + m[4] for x, y in pts]
    ys = [m[1] * x + m[3] * y + m[5] for x, y in pts]
    return min(xs), min(ys), max(xs), max(ys)


for k, (tile_id, swap_img_id) in enumerate(ORDER):
    src = SRC[tile_id]
    ox0, oy0, ox1, oy1 = bounds(src)
    sm = [float(v) for v in src.get("ItemTransform").split()]
    img = src.find("Image")
    im = [float(v) for v in img.get("ItemTransform").split()]
    # image placement in spread coords (frame transform is translation-only)
    ix, iy = im[4] + sm[4], im[5] + sm[5]
    gb = img.find("Properties/GraphicBounds")
    gw, gh = float(gb.get("Right")), float(gb.get("Bottom"))
    k_scale = min(TW / (ox1 - ox0), TH / (oy1 - oy0))
    if swap_img_id:  # same visual width as the logo it replaces
        img = copy.deepcopy(SRC[swap_img_id].find("Image"))
        sim = [float(v) for v in img.get("ItemTransform").split()]
        gb = img.find("Properties/GraphicBounds")
        gw, gh = float(gb.get("Right")), float(gb.get("Bottom"))
        target_w = im[0] * float(SRC[tile_id].find("Image/Properties/GraphicBounds").get("Right")) * k_scale * 1.15
        sx = target_w / gw
        sy = sx * sim[3] / sim[0]
    else:
        img = copy.deepcopy(img)
        sx, sy = im[0] * k_scale, im[3] * k_scale
    col, row = k % 6, k // 6
    nx0, ny0 = 36 + col * (TW + GAP) + PX, ROWS[row] + PY
    # center logo in the new tile
    dw, dh = gw * sx, gh * sy
    img.set("ItemTransform", f"{sx} 0 0 {sy} {nx0 + (TW - dw) / 2} {ny0 + (TH - dh) / 2}")
    tile = copy.deepcopy(src)
    for ch in list(tile):
        if ch.tag in ("Image", "PDF", "EPS"):
            tile.remove(ch)
    tile.append(img)
    tile.set("ItemTransform", "1 0 0 1 0 0")
    pts = list(tile.find("Properties/PathGeometry").iter("PathPointType"))
    corners = [(nx0, ny0), (nx0, ny0 + TH), (nx0 + TW, ny0 + TH), (nx0 + TW, ny0)]
    for p, (cx, cy) in zip(pts, corners):
        for a in ("Anchor", "LeftDirection", "RightDirection"):
            p.set(a, f"{cx} {cy}")
    tile.set("ItemLayer", "u142")
    tile.set("StrokeColor", "Color/Black")
    tile.set("StrokeTint", "20")
    for el in tile.iter():
        if el.get("Self"):
            el.set("Self", new_id())
    for ffo in tile.iter("FrameFittingOption"):
        for a in ("LeftCrop", "TopCrop", "RightCrop", "BottomCrop"):
            ffo.set(a, "0")
    spread.append(tile)
tree.write(SP, xml_declaration=True, encoding="UTF-8", standalone=True)

if os.path.exists(OUT):
    os.remove(OUT)
with zipfile.ZipFile(OUT, "w") as z:
    z.write(os.path.join(BIF, "mimetype"), "mimetype", compress_type=zipfile.ZIP_STORED)
    for root, _, files in os.walk(BIF):
        for fn in sorted(files):
            full = os.path.join(root, fn)
            arc = os.path.relpath(full, BIF)
            if arc != "mimetype":
                z.write(full, arc, compress_type=zipfile.ZIP_DEFLATED)
print("placed", len(ORDER), "tiles")
