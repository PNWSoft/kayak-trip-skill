#!/usr/bin/env python3
"""Build the bundled NOAA SSCOFS mesh index in ../data from the CO-OPS THREDDS server.

Maintainers run this before a release (needs internet):
    python3 build_sscofs_mesh.py
    python3 build_sscofs_mesh.py --file sscofs.t15z.20261005.fields.f001.nc   # a specific source file

SSCOFS (Salish Sea and Columbia River Operational Forecast System) is an
unstructured FVCOM mesh. Currents are given at element (triangle) centers.
This saves one row per element, in element order (row 0 = element 0), with its
center lat/lon, depth (mean of its 3 corner nodes) and how many of its 3 sides are shoreline, so
sscofs_currents.py can find the nearest element offline. Writes
data/sscofs_mesh.csv.gz. Rebuild if NOAA changes the mesh (the element count
is checked at run time).
"""
import argparse
import csv
import datetime as dt
import gzip
import pathlib
import sys
import urllib.request

THREDDS = "https://opendap.co-ops.nos.noaa.gov/thredds"
DATA_DIR = pathlib.Path(__file__).resolve().parent.parent / "data"
OUT = DATA_DIR / "sscofs_mesh.csv.gz"


def get(url, timeout=600):
    req = urllib.request.Request(url, headers={"User-Agent": "kayak-trip-planner mesh builder"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode()


def recent_file():
    """Name and path of a recent fields file (yesterday's 15z f001, which is surely complete)."""
    d = dt.datetime.now(dt.timezone.utc).date() - dt.timedelta(days=1)
    name = f"sscofs.t15z.{d:%Y%m%d}.fields.f001.nc"
    return f"NOAA/SSCOFS/MODELS/{d:%Y/%m/%d}/{name}"


def ascii_vars(path, names):
    """Fetch variables in OPeNDAP ASCII and return {name: flat list of strings}, row-major."""
    text = get(f"{THREDDS}/dodsC/{path}.ascii?{','.join(names)}")
    body = text.split("-" * 45, 1)[1]
    out, cur = {}, None
    for line in body.splitlines():
        line = line.strip()
        if not line:
            continue
        head = line.split("[", 1)[0]
        if head in names and line.endswith("]"):
            cur = head
            out[cur] = []
            continue
        if line.startswith("["):  # 2-D row: "[i], a, b, ..."
            line = line.split(",", 1)[1]
        out[cur].extend(v.strip() for v in line.split(","))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--file", help="fields file name, e.g. sscofs.t15z.20261005.fields.f001.nc")
    args = ap.parse_args()
    if args.file:
        d = args.file.split(".")[2]
        path = f"NOAA/SSCOFS/MODELS/{d[:4]}/{d[4:6]}/{d[6:]}/{args.file}"
    else:
        path = recent_file()
    print(f"Reading mesh from {path} (a few minutes) ...")
    v = ascii_vars(path, ["lonc", "latc", "nbe", "nv", "h"])
    n = len(v["lonc"])
    if not n or len(v["latc"]) != n or len(v["nbe"]) != 3 * n or len(v["nv"]) != 3 * n:
        sys.exit(f"Unexpected sizes: {[(k, len(x)) for k, x in v.items()]}")
    nbe = v["nbe"]  # [three][nele]; 0 means no neighbor on that side (shoreline or open boundary)
    h = [float(x) for x in v["h"]]  # depth at nodes
    nv = [int(x) - 1 for x in v["nv"]]  # [three][nele], 1-based node numbers
    DATA_DIR.mkdir(exist_ok=True)
    with gzip.open(OUT, "wt", newline="") as f:
        w = csv.writer(f)
        w.writerow(["lat", "lon", "depth_m", "shore_sides"])
        for i in range(n):
            lon = float(v["lonc"][i])
            lon = lon - 360 if lon > 180 else lon
            shore = sum(nbe[k * n + i] == "0" for k in range(3))
            depth = sum(h[nv[k * n + i]] for k in range(3)) / 3
            w.writerow([f"{float(v['latc'][i]):.5f}", f"{lon:.5f}", f"{depth:.1f}", shore])
    print(f"{OUT.name}: {n} elements ({OUT.stat().st_size // 1024} KB), built {dt.date.today()} from {path}")


if __name__ == "__main__":
    main()
