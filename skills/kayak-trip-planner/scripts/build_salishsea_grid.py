#!/usr/bin/env python3
"""Build the bundled SalishSeaCast water-cell table in ../data from the UBC ERDDAP server.

Maintainers run this before a release (needs internet):
    python3 build_salishsea_grid.py

It keeps only the grid cells where the currents dataset has values (water), with
each cell's lat/lon and depth, so salishsea_currents.py can find the nearest cell
offline. Writes data/salishsea_grid.csv.gz and data/salishsea_grid.meta.json
(cell count, build date, sources).
"""
import argparse
import csv
import datetime
import gzip
import io
import json
import math
import pathlib
import sys
import urllib.request

ERDDAP = "https://salishsea.eos.ubc.ca/erddap/griddap"
GRID = "ubcSSnBathymetryV21-08"
CURRENTS = "ubcSSfDepthAvgdCurrents1h"
DATA_DIR = pathlib.Path(__file__).resolve().parent.parent / "data"
OUT = DATA_DIR / "salishsea_grid.csv.gz"
META = DATA_DIR / "salishsea_grid.meta.json"


def fetch_csv(url):
    req = urllib.request.Request(url, headers={"User-Agent": "kayak-trip-planner grid builder"})
    with urllib.request.urlopen(req, timeout=600) as r:
        rows = list(csv.reader(io.TextIOWrapper(r, encoding="utf-8")))
    return rows[2:]  # skip header and units rows


def latest_time():
    req = urllib.request.Request(f"{ERDDAP}/{CURRENTS}.das", headers={"User-Agent": "kayak-trip-planner grid builder"})
    with urllib.request.urlopen(req, timeout=120) as r:
        for line in r.read().decode().splitlines():
            if "time_coverage_start" in line:
                return line.split('"')[1]
    sys.exit("Could not read time_coverage_start from the currents dataset.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.parse_args()
    print("Fetching grid lat/lon/depth ...")
    grid = fetch_csv(f"{ERDDAP}/{GRID}.csv?latitude,longitude,bathymetry")
    t = latest_time()
    print(f"Fetching water mask from currents at {t} ...")
    wet = {(r[1], r[2]) for r in fetch_csv(f"{ERDDAP}/{CURRENTS}.csv?VelEast5[({t})][(0):1:(897)][(0):1:(397)]")
           if r[3] not in ("NaN", "")}
    rows = []
    for y, x, lat, lon, depth in grid:
        if (y, x) in wet and not math.isnan(float(lat)):
            rows.append((y, x, f"{float(lat):.5f}", f"{float(lon):.5f}", "" if depth == "NaN" else f"{float(depth):.1f}"))
    if not rows:
        sys.exit("No water cells found; check the source datasets.")
    DATA_DIR.mkdir(exist_ok=True)
    with gzip.open(OUT, "wt", newline="") as f:
        w = csv.writer(f)
        w.writerow(["gridY", "gridX", "lat", "lon", "depth_m"])
        w.writerows(rows)
    META.write_text(json.dumps({"water_cells": len(rows), "built": datetime.date.today().isoformat(), "grid": f"{ERDDAP}/{GRID}",
                                "water_mask": f"{ERDDAP}/{CURRENTS} at {t}"}, indent=2) + "\n")
    print(f"{OUT.name}: {len(rows)} water cells ({OUT.stat().st_size // 1024} KB), built {datetime.date.today()}")


if __name__ == "__main__":
    main()
