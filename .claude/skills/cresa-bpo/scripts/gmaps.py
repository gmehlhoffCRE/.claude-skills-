import os, math, hashlib, requests, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

KEY = os.environ["GKEY"]
OUT = os.environ["LINKS"]
GC = "/tmp/bpo_gtiles"; os.makedirs(GC, exist_ok=True)
NAVY = (0, 30, 90); GOLD = (255, 182, 0); WHITE = (255, 255, 255)
FB = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
STYLE = ["feature:poi|element:labels|visibility:off", "feature:poi.business|visibility:off", "feature:transit.station.bus|visibility:off"]
USE = 608
MASKS = []
MASKF = "/tmp/bpo_logo_mask.png"


def world(lat, lon, z):
    n = 256 * 2 ** z
    s = math.sin(math.radians(lat))
    return (lon + 180) / 360 * n, (0.5 - math.log((1 + s) / (1 - s)) / (4 * math.pi)) * n


def gtile(cx, cy, z, maptype):
    n = 256 * 2 ** z
    lon = cx / n * 360 - 180
    lat = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * cy / n))))
    params = [("center", f"{lat:.7f},{lon:.7f}"), ("zoom", z), ("size", "640x640"), ("scale", 2), ("maptype", maptype)]
    if maptype in ("roadmap", "hybrid"):
        params += [("style", s) for s in STYLE] + ([("style", "feature:poi|visibility:off")] if maptype == "hybrid" else [])
    p = f"{GC}/{hashlib.md5(repr(params).encode()).hexdigest()}.png"
    if not os.path.exists(p):
        r = requests.get("https://maps.googleapis.com/maps/api/staticmap", params=params + [("key", KEY)], timeout=60)
        r.raise_for_status(); assert r.headers["content-type"].startswith("image"), r.text[:200]
        open(p, "wb").write(r.content)
    return Image.open(p).convert("RGB")


class GMap:
    def __init__(self, lat, lon, z, w_pt, h_pt, ppt=1.0, dpi=300, maptype="roadmap"):
        self.z, self.ppt = z, ppt
        wpx, hpx = w_pt * ppt, h_pt * ppt
        cx, cy = world(lat, lon, z)
        self.x0, self.y0 = cx - wpx / 2, cy - hpx / 2
        cols, rows = int(np.ceil(wpx / 640)), int(np.ceil(hpx / USE))
        mos = Image.new("RGB", (int(np.ceil(wpx * 2)), int(np.ceil(hpx * 2))))
        for j in range(rows):
            for i in range(cols):
                t = gtile(self.x0 + i * 640 + 320, self.y0 + j * USE + 320, z, maptype)
                mos.paste(t.crop((0, 0, 1280, USE * 2)), (i * 1280, j * USE * 2))
        W2, H2 = mos.size
        ref = gtile(self.x0 + 320, self.y0 + hpx - 320, z, maptype)
        pw, ph = 180, 70
        logo = ref.crop((0, 1280 - ph, pw, 1280)); base = mos.crop((0, H2 - ph, pw, H2))
        diff = np.abs(np.asarray(logo).astype(int) - np.asarray(base).astype(int)).sum(2)
        raw = ((diff > 40) * 255).astype("uint8"); MASKS.append(raw)
        if os.path.exists(MASKF): raw = np.asarray(Image.open(MASKF))
        mask = Image.fromarray(raw).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(0.8))
        k = 0.55; sz = (int(pw * k), int(ph * k))
        mos.paste(logo.resize(sz, Image.LANCZOS), (6, H2 - sz[1] - 2), mask.resize(sz, Image.LANCZOS))
        self.S = dpi / 72 / ppt
        self.img = mos.resize((round(wpx * self.S), round(hpx * self.S)), Image.LANCZOS).convert("RGBA")
        self.pt = dpi / 72
        self.d = ImageDraw.Draw(self.img)
        img_t = "Imagery \u00a92026 Airbus, Maxar Technologies, Vexcel Imaging US, Inc."
        map_t = "Map data \u00a92026 Google" + (", INEGI" if z <= 11 else "")
        self.attribution({"satellite": img_t, "hybrid": img_t + ", " + map_t}.get(maptype, map_t), 3.2 if w_pt < 300 else 3.8)

    def xy(self, lat, lon):
        x, y = world(lat, lon, self.z)
        return (x - self.x0) * self.S, (y - self.y0) * self.S

    def page_xy(self, lat, lon):
        x, y = self.xy(lat, lon); return x / self.pt, y / self.pt

    def font(self, size_pt, bold=True):
        return ImageFont.truetype(FB if bold else FR, round(size_pt * self.pt))

    def attribution(self, text, size):
        f = self.font(size, bold=False); W, H = self.img.size
        ov = Image.new("RGBA", self.img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        tw = d.textlength(text, font=f); p = 1.6 * self.pt
        d.rectangle([W - tw - 2 * p, H - f.size - 2 * p, W, H], fill=(255, 255, 255, 120))
        d.text((W - tw - p, H - p), text, font=f, fill=(95, 95, 95, 230), anchor="ls")
        self.img.alpha_composite(ov)

    def square(self, lat, lon, label, size=15, dx=0):
        x, y = self.xy(lat, lon); x += dx * self.pt; h = size * self.pt / 2
        self.d.rectangle([x - h, y - h, x + h, y + h], fill=NAVY, outline=WHITE, width=max(2, int(self.pt)))
        self.d.text((x, y), label, font=self.font(size * 0.62), fill=WHITE, anchor="mm")

    def pin(self, lat, lon, size=22, label=None, label_side="right"):
        x, y = self.xy(lat, lon); s = size * self.pt; r = s * 0.36; cy = y - s + r
        self.d.polygon([(x, y), (x - r * 0.92, cy + r * 0.45), (x + r * 0.92, cy + r * 0.45)], fill=NAVY)
        self.d.ellipse([x - r, cy - r, x + r, cy + r], fill=NAVY)
        rr = r * 0.42; self.d.ellipse([x - rr, cy - rr, x + rr, cy + rr], fill=GOLD)
        if label:
            f = self.font(8.5); tw = self.d.textlength(label, font=f); ph, pv = 8 * self.pt, 4.5 * self.pt; bh = f.size + 2 * pv
            if label_side == "left": bx1 = x - r - 6 * self.pt; bx0 = bx1 - tw - 2 * ph
            else: bx0 = x + r + 6 * self.pt; bx1 = bx0 + tw + 2 * ph
            self.d.rectangle([bx0, cy - bh / 2, bx1, cy + bh / 2], fill=NAVY)
            self.d.text(((bx0 + bx1) / 2, cy), label, font=f, fill=GOLD, anchor="mm")

    def poly(self, ring, fill=(255, 182, 0, 70), width=2.0):
        pts = [self.xy(la, lo) for lo, la in ring]
        ov = Image.new("RGBA", self.img.size, (0, 0, 0, 0)); ImageDraw.Draw(ov).polygon(pts, fill=fill)
        self.img.alpha_composite(ov)
        self.d.line(pts + [pts[0]], fill=GOLD, width=round(width * self.pt), joint="curve")

    def ring(self, lat, lon, miles, label):
        x, y = self.xy(lat, lon)
        r = miles * 1609.344 / (156543.03392 * math.cos(math.radians(lat)) / 2 ** self.z) * self.S
        self.d.ellipse([x - r, y - r, x + r, y + r], outline=NAVY, width=round(1.6 * self.pt))
        f = self.font(7.5); tw = self.d.textlength(label, font=f); ph, pv = 5 * self.pt, 3 * self.pt
        self.d.rectangle([x - tw / 2 - ph, y - r - f.size / 2 - pv, x + tw / 2 + ph, y - r + f.size / 2 + pv], fill=NAVY)
        self.d.text((x, y - r), label, font=f, fill=WHITE, anchor="mm")

    def save(self, name):
        self.img.convert("RGB").save(OUT + name, dpi=(self.pt * 72, self.pt * 72))


def finish_mask():
    if not os.path.exists(MASKF) and MASKS:
        Image.fromarray(np.minimum.reduce(MASKS)).save(MASKF); return True
    return False


def mpp(lat, z):
    """meters per Google css pixel"""
    return 156543.03392 * math.cos(math.radians(lat)) / 2 ** z


def fit(points, w_pt, h_pt, fill=0.7, min_ppt=1.0, zmax=20, zmin=5):
    """Pick (center_lat, center_lon, z, ppt) so all (lat, lon) points fit in fill of the frame,
    using the lowest css-px-per-point that is still >= min_ppt (sharp imagery, readable labels)."""
    lats = [p[0] for p in points]; lons = [p[1] for p in points]
    clat, clon = (min(lats) + max(lats)) / 2, (min(lons) + max(lons)) / 2
    bh = max((max(lats) - min(lats)) * 110574, 30); bw = max((max(lons) - min(lons)) * 111320 * math.cos(math.radians(clat)), 30)
    m_per_pt = max(bw / (fill * w_pt), bh / (fill * h_pt))
    for z in range(zmin, zmax + 1):
        ppt = m_per_pt / mpp(clat, z)
        if ppt >= min_ppt:
            return clat, clon, z, ppt
    return clat, clon, zmax, m_per_pt / mpp(clat, zmax)
