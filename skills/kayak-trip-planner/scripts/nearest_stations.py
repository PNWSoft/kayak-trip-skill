#!/usr/bin/env python3
"""Find the nearest NOAA tide stations, current stations and NDBC buoys to a point.

Works offline from the bundled snapshot in ../data (built by build_station_data.py).

    python3 nearest_stations.py --lat 48.655 --lon -122.49
    python3 nearest_stations.py --lat 48.655 --lon -122.49 --kind current --n 3 --json
"""
import argparse
import csv
import json
import math
import pathlib
import sys

DATA_DIR = pathlib.Path(__file__).resolve().parent.parent / "data"
FILES = {"tide": "tide_stations.csv", "current": "current_stations.csv", "buoy": "ndbc_stations.csv"}
COMPASS = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]


def distance_bearing(lat1, lon1, lat2, lon2):
    """Great-circle distance in statute miles and compass bearing from point 1 to point 2."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dl = math.radians(lon2 - lon1)
    a = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    miles = 3958.8 * 2 * math.asin(math.sqrt(a))
    y = math.sin(dl) * math.cos(p2)
    x = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dl)
    deg = (math.degrees(math.atan2(y, x)) + 360) % 360
    return miles, COMPASS[int((deg + 11.25) // 22.5) % 16]


def nearest(kind, lat, lon, n, max_mi):
    path = DATA_DIR / FILES[kind]
    if not path.exists():
        return None
    out = []
    with path.open() as f:
        for row in csv.DictReader(f):
            mi, brg = distance_bearing(lat, lon, float(row["lat"]), float(row["lon"]))
            if max_mi is None or mi <= max_mi:
                row.update(distance_mi=round(mi, 1), bearing=brg)
                out.append(row)
    return sorted(out, key=lambda r: r["distance_mi"])[:n]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--lat", type=float, required=True)
    ap.add_argument("--lon", type=float, required=True, help="negative for west")
    ap.add_argument("--kind", choices=["tide", "current", "buoy", "all"], default="all")
    ap.add_argument("--n", type=int, default=5, help="how many per kind (default 5)")
    ap.add_argument("--max-mi", type=float, help="ignore stations farther than this")
    ap.add_argument("--json", action="store_true", help="print JSON instead of a table")
    args = ap.parse_args()
    if not (-90 <= args.lat <= 90 and -180 <= args.lon <= 180):
        sys.exit("lat/lon out of range")

    kinds = list(FILES) if args.kind == "all" else [args.kind]
    results, missing = {}, []
    for k in kinds:
        r = nearest(k, args.lat, args.lon, args.n, args.max_mi)
        if r is None:
            missing.append(FILES[k])
        else:
            results[k] = r

    if args.json:
        print(json.dumps({"results": results, "missing_data": missing}, indent=2))
    else:
        for k, rows in results.items():
            print(f"\n{k.upper()} stations nearest {args.lat}, {args.lon}")
            if not rows:
                print("  none within range")
            for r in rows:
                extra = f"  bin {r['bin']}" if k == "current" else ""
                print(f"  {r['id']:<10} {r['distance_mi']:>6} mi {r['bearing']:<3}  {r['name']}{extra}")
    if missing:
        print(f"\nMissing data files in {DATA_DIR}: {', '.join(missing)}. "
              "Run build_station_data.py, or ask the user for station IDs.", file=sys.stderr)
        if not results:
            sys.exit(1)


if __name__ == "__main__":
    main()
