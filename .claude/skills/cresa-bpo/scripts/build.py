"""Build a Cresa BPO package from a property JSON.

  GKEY=<google key> python build.py property.json --work /home/claude/bpo_<slug> [--maps all|none|site,aerial,location,inset,comps,rings]

Produces <work>/out/<Address> - BPO/{<Address> - BPO.idml, Links/, <Address> - BPO - Preview.pdf} and
<work>/<Address_slug>_BPO_InDesign.zip. Prints any text overset / table overflow warnings from the preview pass.
"""
import os, sys, json, shutil, argparse, subprocess, math, zipfile
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)


def rings_of(fc):
    out = []
    for f in fc["features"]:
        g = f["geometry"]
        out.append(g["coordinates"][0] if g["type"] == "Polygon" else g["coordinates"][0][0])
    return out


def build_maps(D, links, work, which):
    sys.path.insert(0, HERE)
    os.environ["LINKS"] = links
    import importlib, gmaps
    importlib.reload(gmaps)
    from gmaps import GMap, fit
    S = (D["site"]["lat"], D["site"]["lon"])
    rings = rings_of(json.load(open(os.path.join(work, D["parcels_geojson"])))) if D.get("parcels_geojson") else []
    mo = D.get("map_options", {})
    pts = [(la, lo) for r in rings for lo, la in r]
    if not pts:  # no parcel outline: frame a box around the pin so maps are not zoomed to the max
        rm = mo.get("pin_radius_m", 70); dla = rm / 111320; dlo = rm / (111320 * math.cos(math.radians(S[0])))
        pts = [(S[0] - dla, S[1] - dlo), (S[0] + dla, S[1] + dlo)]
    geom = {}
    if "site" in which:
        clat, clon, z, ppt = fit(pts, 294.2, 468, fill=mo.get("site_fill", 0.62), min_ppt=1.2, zmax=19)
        m = GMap(clat, clon, z, 294.2, 468, ppt=ppt, maptype="hybrid")
        for r in rings: m.poly(r)
        if not rings: m.pin(*S, size=24)
        m.save("map_site_parcels.png")
    if "aerial" in which:
        clat, clon, z, ppt = fit(pts, 792, 612, fill=mo.get("aerial_fill", 0.62), min_ppt=1.6, zmax=20)
        # shift so the parcels sit right of center (title + callouts live on the left)
        shift_pt = mo.get("aerial_shift_pt", 90)
        from gmaps import mpp
        clon -= shift_pt * ppt * mpp(clat, z) / (111320 * math.cos(math.radians(clat)))
        m = GMap(clat, clon, z, 792, 612, ppt=ppt, maptype="satellite")
        for r in rings: m.poly(r, fill=(255, 182, 0, 0), width=2.5)
        if not rings: m.pin(*S, size=22)  # no parcel outline: mark the building
        m.save("aerial_overhead.png")
        pp = [m.page_xy(la, lo) for la, lo in pts]
        geom = {"centroids": [m.page_xy(sum(p[1] for p in r) / len(r), sum(p[0] for p in r) / len(r)) for r in rings],
                "center": m.page_xy(sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)),
                "minx": min(p[0] for p in pp), "maxx": max(p[0] for p in pp), "miny": min(p[1] for p in pp), "maxy": max(p[1] for p in pp)}
        geom["labels"] = road_labels(D, m)
        geom["map"] = {"z": z, "x0": m.x0, "y0": m.y0, "S": m.S, "pt": m.pt}  # lets page points be converted back to lat/lon
        json.dump(geom, open(os.path.join(work, "geom.json"), "w"))
    if "location" in which:
        m = GMap(*S, mo.get("location_zoom", 13), 500.5, 463.1, ppt=1.2)
        m.pin(*S, size=26, label="Subject", label_side=mo.get("location_label_side", "right")); m.save("map_location.png")
    if "inset" in which:
        c = ((S[0] + 29.76) / 2, (S[1] - 95.37) / 2)
        z = 9 if abs(S[0] - 29.76) < 0.25 and abs(S[1] + 95.37) < 0.3 else 8
        m = GMap(*c, z, 183.6, 153.7, ppt=1.3); m.pin(*S, size=15); m.save("map_inset.png")
    if "comps" in which:
        comps = [c for c in D.get("comps", []) if c.get("lat")]
        import bpo_spec_sort
        comps = bpo_spec_sort.sort(comps)
        cpts = [(c["lat"], c["lon"]) for c in comps] + [S]
        if len(cpts) > 1:
            clat, clon, z, ppt = fit(cpts, 792, 480.3, fill=0.78, min_ppt=1.25, zmax=15)
        else:
            clat, clon, z, ppt = S[0], S[1], 11, 1.35
        m = GMap(clat, clon, z, 792, 480.3, ppt=ppt)
        seen = {}
        for i, c in enumerate(comps, 1):
            k = (round(c["lat"], 5), round(c["lon"], 5)); dx = 18 * seen.get(k, 0); seen[k] = seen.get(k, 0) + 1
            m.square(c["lat"], c["lon"], str(i), size=17, dx=dx)
        m.pin(*S, size=26, label="Subject", label_side=mo.get("comps_label_side", "right")); m.save("map_comps.png")
    if "rings" in which:
        m = GMap(*S, 12, 358, 466, ppt=1.55)
        for mi, lab in ((5, "5 Miles"), (3, "3 Miles"), (1, "1 Mile")): m.ring(*S, mi, lab)
        m.pin(*S, size=22); m.save("map_demographics_rings.png")
    return gmaps


def crop_to(src, w_pt, h_pt, focus=(0.5, 0.5), zoom=1.0):
    """Crop an image to the frame's aspect ratio around a focus point (fractions of width/height).
    zoom > 1 crops tighter (1.3 = building 30% larger in the frame), at the cost of placed resolution."""
    im = Image.open(src).convert("RGB"); w, h = im.size; ar = w_pt / h_pt
    cw, ch = (h * ar, h) if w / h > ar else (w, w / ar)
    cw, ch = int(cw / max(zoom, 1)), int(ch / max(zoom, 1))
    x0 = min(max(0, int(w * focus[0] - cw / 2)), w - cw); y0 = min(max(0, int(h * focus[1] - ch / 2)), h - ch)
    return im.crop((x0, y0, x0 + cw, y0 + ch))


FRAMES = {"cover_photo": ("cover_photo.jpg", 718.8, 473.5), "intro_photo": ("intro_photo.jpg", 792, 327)}


def snap(pts):
    """Snap (lat, lon) points to the nearest road centerline with the Google Roads API; returns the input on failure."""
    key = os.environ.get("GKEY")
    if not key: return pts
    import requests
    try:
        r = requests.get("https://roads.googleapis.com/v1/nearestRoads", params={"points": "|".join(f"{a},{o}" for a, o in pts), "key": key}, timeout=30).json()
        out = list(pts)
        for sp in r.get("snappedPoints", []):
            i = sp["originalIndex"]
            if out[i] is pts[i]: out[i] = (sp["location"]["latitude"], sp["location"]["longitude"])
        return out
    except Exception:
        return pts


def road_labels(D, m):
    """Each traffic_counts / road_labels item gives two points along its road ('a' and 'b' as [lat, lon]).
    The label is centered between them and rotated to the road's angle, kept readable (-90..90 degrees)."""
    out = []
    items = [("traffic", t) for t in D.get("traffic_counts", [])] + [("road", t) for t in D.get("road_labels", [])]
    for kind, t in items:
        if "a" not in t or "b" not in t: continue
        a, b = (tuple(t["a"]), tuple(t["b"])) if t.get("snap") is False else snap([tuple(t["a"]), tuple(t["b"])])
        (x1, y1), (x2, y2) = m.page_xy(*a), m.page_xy(*b)
        ang = math.degrees(math.atan2(y2 - y1, x2 - x1))
        ang = (ang + 90) % 180 - 90
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        if not (0 < cx < 792 and 0 < cy < 612): print(f"NOTE {kind} label off the aerial: {t.get('name') or t.get('road')}")
        out.append(dict(kind=kind, x=cx, y=cy, angle=round(ang, 2), vpd=t.get("vpd"), name=t.get("name") or t.get("road")))
    return out


def prep_photos(D, work, links):
    for key, (name, wpt, hpt) in FRAMES.items():
        spec = D.get(key)
        if not spec: continue
        spec = {"src": spec} if isinstance(spec, str) else spec
        src = spec["src"] if os.path.isabs(spec["src"]) else os.path.join(work, spec["src"])
        im = crop_to(src, wpt, hpt, tuple(spec.get("focus", (0.5, 0.5))), spec.get("zoom", 1.0))
        tw = int(wpt / 72 * 300)  # 300 dpi at placed size
        if im.size[0] < tw: print(f"NOTE {key}: source is {im.size[0]}px wide, about {int(im.size[0] / wpt * 72)} dpi at placed size (300 recommended)")
        im.resize((min(tw, im.size[0]) if im.size[0] < tw else tw, int((min(tw, im.size[0]) if im.size[0] < tw else tw) * hpt / wpt)), Image.LANCZOS).save(os.path.join(links, name), quality=92, dpi=(300, 300))
        D[key + "_file"] = name
    import bpo_spec_sort
    comps = bpo_spec_sort.sort(D.get("comps") or [])
    per = D.get("comps_per_page") or (5 if len(comps) <= 5 else -(-len(comps) // -(-len(comps) // 5)))
    for k in range(0, len(comps), per):
        chunk = comps[k:k + per]; cw = (708.6 - 92.5) / len(chunk) - 4; ar = cw / 80
        for i, c in enumerate(chunk):
            src = c.get("photo_src")
            if not src: continue
            src = src if os.path.isabs(src) else os.path.join(work, src)
            im = Image.open(src).convert("RGB"); w, h = im.size
            if w / h > ar: nw = int(h * ar); im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
            else: nh = int(w / ar); im = im.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
            name = f"comp{k + i + 1}.png"
            im.resize((int(cw * 6), 480), Image.LANCZOS).save(os.path.join(links, name), dpi=(432, 432))
            c["photo"] = name
    return D


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("property"); ap.add_argument("--work", required=True); ap.add_argument("--maps", default="all")
    a = ap.parse_args()
    work = os.path.abspath(a.work); links = os.path.join(work, "Links") + "/"; low = os.path.join(work, "low") + "/"
    os.makedirs(links, exist_ok=True); os.makedirs(low, exist_ok=True)
    shutil.copy(os.path.join(SKILL, "assets", "cresa_logo.png"), links)
    sys.path.insert(0, HERE)
    D = json.load(open(a.property))
    which = [] if a.maps == "none" else (["site", "aerial", "location", "inset", "comps", "rings"] if a.maps == "all" else a.maps.split(","))
    if D.get("skip_aerial") and "aerial" in which: which.remove("aerial")
    if which:
        g = build_maps(D, links, work, which)
        if g.finish_mask():  # first run on this machine: logo mask learned, rebuild for a clean Google logo
            build_maps(D, links, work, which)
    D = prep_photos(D, work, links)
    resolved = os.path.join(work, "property.resolved.json"); json.dump(D, open(resolved, "w"), indent=1)
    name = f'{D["address"]} - BPO'
    out = os.path.join(work, "out", name); shutil.rmtree(os.path.join(work, "out"), ignore_errors=True); os.makedirs(os.path.join(out, "Links"))
    for f in os.listdir(links):
        if f.endswith((".png", ".jpg")): shutil.copy(links + f, os.path.join(out, "Links"))
    env = dict(os.environ, PROPERTY=resolved, GEOM=os.path.join(work, "geom.json"), LINKS=links, PYTHONPATH=HERE)
    subprocess.run([sys.executable, os.path.join(HERE, "idml.py"), os.path.join(out, name + ".idml")], env=env, check=True)
    for f in os.listdir(links):  # light preview copies
        im = Image.open(links + f)
        if f == "cresa_logo.png": im.save(low + f)
        else:
            im = im.convert("RGB"); im.thumbnail((1600, 1600)); im.save(low + f.rsplit(".", 1)[0] + ".jpg", "JPEG", quality=82)
    env["LINKS"] = low
    r = subprocess.run([sys.executable, os.path.join(HERE, "preview.py"), os.path.join(out, name + " - Preview.pdf")], env=env, capture_output=True, text=True)
    print(r.stdout, r.stderr)
    zp = os.path.join(work, D["address"].replace(" ", "_") + "_BPO_InDesign.zip")
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(out):
            for f in files:
                p = os.path.join(root, f); z.write(p, os.path.relpath(p, os.path.join(work, "out")))
    print("PACKAGE", zp); print("PREVIEW", os.path.join(out, name + " - Preview.pdf"))


if __name__ == "__main__":
    main()
