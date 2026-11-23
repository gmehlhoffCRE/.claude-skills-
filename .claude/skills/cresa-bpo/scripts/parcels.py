"""Parcel outlines and geocoding for Houston-area BPOs.

Usage:
  python parcels.py geocode "13550 S Gessner Rd, Missouri City, TX 77489"
  python parcels.py hcad 0041760000227 1310110010001 --out parcels.geojson      # Harris County, by HCAD account #
  python parcels.py near 29.6268 -95.5408 --county fortbend --dist 80            # list parcels near a point (pick the right ones)
  python parcels.py fbcad 3518-01-000-0010-907 --out parcels.geojson             # Fort Bend, by FBCAD property #

Outputs GeoJSON (EPSG:4326). Always print owner/acreage so the user can confirm which parcels are in the sale.
"""
import sys, os, json, argparse, requests

HCAD = "https://www.gis.hctx.net/arcgis/rest/services/HCAD/Parcels/MapServer/0/query"
FBCAD = "https://gisweb.fbcad.org/arcgis/rest/services/Hosted/FBCADPublicData/FeatureServer/0/query"
KEEP = {"hcad": ["HCAD_NUM", "owner_name_1", "site_str_num", "site_str_name", "site_str_sfx", "acreage_1", "land_sqft", "new_owner_date"],
        "fbcad": ["propnumber", "ownername", "situs", "landsizeac", "landsizeft", "legal", "deeddate", "impvalue", "landvalue"]}


def query(url, **params):
    p = {"outFields": "*", "outSR": 4326, "f": "geojson"}; p.update(params)
    r = requests.get(url, params=p, timeout=60); r.raise_for_status()
    return r.json()


def show(fc, kind):
    for f in fc.get("features", []):
        pr = f["properties"]
        print(" | ".join(f"{k}={pr.get(k)}" for k in KEEP[kind] if pr.get(k) not in (None, "", " ")))


def geocode(addr):
    r = requests.get("https://geocoding.geo.census.gov/geocoder/locations/onelineaddress",
                     params={"address": addr, "benchmark": "Public_AR_Current", "format": "json"}, timeout=30).json()
    m = r["result"]["addressMatches"]
    if m:
        c = m[0]["coordinates"]; return m[0]["matchedAddress"], c["y"], c["x"], "census"
    key = os.environ.get("GKEY")
    if key:  # Census misses frontage-road style addresses (e.g. "W Sam Houston Pkwy N"); Google handles them
        g = requests.get("https://maps.googleapis.com/maps/api/geocode/json", params={"address": addr, "key": key}, timeout=30).json()
        if g.get("results"):
            loc = g["results"][0]["geometry"]["location"]; return g["results"][0]["formatted_address"], loc["lat"], loc["lng"], "google"
    return None


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["geocode", "hcad", "fbcad", "near"])
    ap.add_argument("args", nargs="+")
    ap.add_argument("--out"); ap.add_argument("--county", default="harris"); ap.add_argument("--dist", type=float, default=80)
    a = ap.parse_args()
    if a.cmd == "geocode":
        res = geocode(" ".join(a.args)); print(res); sys.exit(0 if res else 1)
    if a.cmd == "hcad":
        ids = ",".join(f"'{i}'" for i in a.args)
        fc = query(HCAD, where=f"HCAD_NUM IN ({ids})"); show(fc, "hcad")
    elif a.cmd == "fbcad":
        ids = ",".join(f"'{i}'" for i in a.args)
        fc = query(FBCAD, where=f"propnumber IN ({ids})"); show(fc, "fbcad")
    else:
        lat, lon = map(float, a.args[:2]); kind = "fbcad" if a.county.startswith("fort") else "hcad"
        fc = query(FBCAD if kind == "fbcad" else HCAD, geometry=f"{lon},{lat}", geometryType="esriGeometryPoint", inSR=4326,
                   spatialRel="esriSpatialRelIntersects", distance=a.dist, units="esriSRUnit_Meter")
        show(fc, kind)
    if a.out:
        json.dump(fc, open(a.out, "w")); print("saved", a.out, len(fc.get("features", [])), "features")
