#!/usr/bin/env python3
"""Build the bundled station snapshot in ../data from NOAA sources.

Maintainers run this before a release (needs internet):
    python3 build_station_data.py

Without internet, download the three source files in a browser, put them in
one folder with these names, and run with --from-dir:
    current.json   https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations.json?type=currentpredictions
    tide.json      https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations.json?type=tidepredictions
    ndbc.xml       https://www.ndbc.noaa.gov/activestations.xml
    python3 build_station_data.py --from-dir ~/Downloads/noaa
"""
import argparse
import csv
import datetime
import json
import pathlib
import sys
import urllib.request
import xml.etree.ElementTree as ET

SOURCES = {
    "current.json": "https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations.json?type=currentpredictions",
    "tide.json": "https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations.json?type=tidepredictions",
    "ndbc.xml": "https://www.ndbc.noaa.gov/activestations.xml",
}
DATA_DIR = pathlib.Path(__file__).resolve().parent.parent / "data"


def load(name, from_dir):
    if from_dir:
        return (pathlib.Path(from_dir).expanduser() / name).read_bytes()
    req = urllib.request.Request(SOURCES[name], headers={"User-Agent": "kayak-trip-planner station builder"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def build_current(raw):
    # One row per station: keep the shallowest predicted depth, closest to what a kayak feels.
    # Bins are numbered up from the bottom (bin 1 is deepest), so choose by depth, not bin number;
    # with no depths, the highest bin is the shallowest.
    def shallower(new, old):
        if new["depth_ft"] != "" and old["depth_ft"] != "":
            return new["depth_ft"] < old["depth_ft"]
        return new["bin"] > old["bin"]

    best = {}
    for s in json.loads(raw)["stations"]:
        lat, lon = num(s.get("lat")), num(s.get("lng"))
        if lat is None or lon is None:
            continue
        b = s.get("currbin") or 1
        row = {"id": s["id"], "bin": b, "depth_ft": s.get("depth") if s.get("depth") is not None else ""}
        if s["id"] not in best or shallower(row, best[s["id"]]):
            best[s["id"]] = {
                "id": s["id"], "name": (s.get("name") or "").strip(), "lat": lat, "lon": lon,
                "bin": b, "depth_ft": s.get("depth") if s.get("depth") is not None else "",
                "type": s.get("type") or "",
            }
    return sorted(best.values(), key=lambda r: r["id"])


def build_tide(raw):
    rows = []
    for s in json.loads(raw)["stations"]:
        lat, lon = num(s.get("lat")), num(s.get("lng"))
        if lat is None or lon is None:
            continue
        rows.append({"id": s["id"], "name": (s.get("name") or "").strip(), "lat": lat, "lon": lon,
                     "state": s.get("state") or "", "type": s.get("type") or ""})
    return sorted(rows, key=lambda r: r["id"])


def build_ndbc(raw):
    rows = []
    for st in ET.fromstring(raw).iter("station"):
        a = st.attrib
        lat, lon = num(a.get("lat")), num(a.get("lon"))
        if lat is None or lon is None or a.get("met") != "y":
            continue  # keep stations that report weather (wind)
        rows.append({"id": a["id"].upper(), "name": (a.get("name") or "").strip(), "lat": lat, "lon": lon,
                     "type": a.get("type") or "", "owner": a.get("owner") or ""})
    return sorted(rows, key=lambda r: r["id"])


def write(path, rows):
    if not rows:
        sys.exit(f"No rows for {path.name}; check the source file.")
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"{path.name}: {len(rows)} stations")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--from-dir", help="read current.json, tide.json and ndbc.xml from this folder instead of downloading")
    args = ap.parse_args()
    DATA_DIR.mkdir(exist_ok=True)
    counts = {}
    for name, builder, out in (("current.json", build_current, "current_stations.csv"),
                               ("tide.json", build_tide, "tide_stations.csv"),
                               ("ndbc.xml", build_ndbc, "ndbc_stations.csv")):
        rows = builder(load(name, args.from_dir))
        write(DATA_DIR / out, rows)
        counts[out] = len(rows)
    stamp = datetime.date.today().isoformat()
    (DATA_DIR / "SNAPSHOT.txt").write_text(
        f"Station snapshot built {stamp}\n" + "".join(f"{k}: {v}\n" for k, v in counts.items())
        + "Sources:\n" + "".join(f"  {u}\n" for u in SOURCES.values()))
    print(f"Snapshot date {stamp} written to {DATA_DIR / 'SNAPSHOT.txt'}")


if __name__ == "__main__":
    main()
