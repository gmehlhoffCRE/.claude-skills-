"""Parcel outlines and geocoding for Houston-area BPOs.

Usage:
  python parcels.py geocode "13550 S Gessner Rd, Missouri City, TX 77489"
  python parcels.py hcad 0041760000227 1310110010001 --out parcels.geojson      # Harris County, by HCAD account #
  python parcels.py near 29.6268 -95.5408 --county fortbend --dist 80            # list parcels near a point (pick the right ones)
  python parcels.py fbcad 3518-01-000-0010-907 --out parcels.geojson             # Fort Bend, by FBCAD property #
  python parcels.py mcad 215605 --out parcels.geojson                             # Montgomery, by MCAD pid
  python parcels.py wcad 20202 --out parcels.geojson                              # Waller, by WCAD prop_id (lots are merged)
  python parcels.py near 30.1677 -95.4639 --county montgomery --dist 30           # also: --county waller

Outputs GeoJSON (EPSG:4326). Always print owner/acreage so the user can confirm which parcels are in the sale.
"""
import sys, os, json, argparse, requests

HCAD = "https://www.gis.hctx.net/arcgis/rest/services/HCAD/Parcels/MapServer/0/query"
# FBCAD's own GIS server now requires a token; this public ArcGIS Online copy of FBCAD Public Data does not.
FBCAD = "https://services2.arcgis.com/D4saGHECICkCeoJm/arcgis/rest/services/FBCAD_Public_Data/FeatureServer/0/query"
MCAD = "https://services1.arcgis.com/PRoAPGnMSUqvTrzq/arcgis/rest/services/Tax_Parcel_view/FeatureServer/0/query"
WCAD = "https://services5.arcgis.com/VPrBcXpTAXqMTZ3Y/arcgis/rest/services/Waller_County_2025_Parcels/FeatureServer/0/query"
KEEP = {"hcad": ["HCAD_NUM", "owner_name_1", "site_str_num", "site_str_name", "site_str_sfx", "acreage_1", "land_sqft", "new_owner_date"],
        "fbcad": ["PROPNUMBER", "OWNERNAME", "SITUS", "LANDSIZEAC", "LANDSIZEFT", "QUICKREFID"],
        "mcad": ["pid", "ownerName", "situs", "legalDescription", "imprvMainArea", "imprvActualYearBuilt"],
        "wcad": ["prop_id", "geo_id", "situs_num", "situs_st_1", "legal_desc", "addr_line1"]}


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
    ap.add_argument("cmd", choices=["geocode", "hcad", "fbcad", "mcad", "wcad", "near"])
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
        fc = query(FBCAD, where=f"PROPNUMBER IN ({ids})"); show(fc, "fbcad")
    elif a.cmd == "mcad":
        fc = query(MCAD, where=f"pid IN ({','.join(a.args)})"); show(fc, "mcad")
    elif a.cmd == "wcad":
        fc = query(WCAD, where=f"prop_id IN ({','.join(a.args)})")
        from shapely.geometry import shape, mapping
        from shapely.ops import unary_union
        by = {}
        for f in fc.get("features", []): by.setdefault(f["properties"]["prop_id"], []).append(f)
        fc = {"type": "FeatureCollection", "features": [  # WCAD splits one account into a polygon per lot
            {"type": "Feature", "properties": fs[0]["properties"], "geometry": mapping(unary_union([shape(f["geometry"]) for f in fs]).buffer(0))}
            for fs in by.values()]}
        show(fc, "wcad")
    else:
        lat, lon = map(float, a.args[:2])
        kind = {"fort": "fbcad", "mont": "mcad", "wall": "wcad"}.get(a.county[:4], "hcad")
        fc = query({"fbcad": FBCAD, "mcad": MCAD, "wcad": WCAD, "hcad": HCAD}[kind], geometry=f"{lon},{lat}", geometryType="esriGeometryPoint", inSR=4326,
                   spatialRel="esriSpatialRelIntersects", distance=a.dist, units="esriSRUnit_Meter")
        show(fc, kind)
    if a.out:
        json.dump(fc, open(a.out, "w")); print("saved", a.out, len(fc.get("features", [])), "features")
