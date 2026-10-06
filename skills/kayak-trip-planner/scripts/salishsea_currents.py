#!/usr/bin/env python3
"""Modeled surface currents at a point in the Salish Sea, from SalishSeaCast (UBC).

Finds the nearest model water cell from the bundled table in ../data (offline),
checks it is close enough to mean something, then fetches the hourly forecast.

    python3 salishsea_currents.py --lat 48.6555 --lon -122.498 --date 2026-10-06
    python3 salishsea_currents.py --lat 48.6555 --lon -122.498 --date 2026-10-06 --start 10:00 --hours 4 --json
    python3 salishsea_currents.py --lat 48.6555 --lon -122.498 --date 2026-10-06 --url-only

--url-only prints the cell checks and the data URLs without fetching, for
environments where the shell has no internet but a web-fetch tool does.

Values are hourly averages; each time is the centre of its hour (10:30 = 10:00-11:00).

Exit codes: 0 ok, 1 data unavailable, 2 no usable cell (outside the model or too far),
3 trip window past the forecast.
"""
import argparse
import csv
import datetime as dt
import gzip
import json
import math
import pathlib
import sys
import urllib.request
from zoneinfo import ZoneInfo

ERDDAP = "https://salishsea.eos.ubc.ca/erddap/griddap/ubcSSfDepthAvgdCurrents1h"
GRID_FILE = pathlib.Path(__file__).resolve().parent.parent / "data" / "salishsea_grid.csv.gz"
COMPASS = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
CELL_M = 500  # nominal model resolution
GOOD_M = 400  # a point inside a water cell is at most ~350 m from its center


def meters(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lon2 - lon1) / 2) ** 2
    return 6371000 * 2 * math.asin(math.sqrt(a))


def nearest_cell(lat, lon):
    cells = {}
    best = None
    with gzip.open(GRID_FILE, "rt") as f:
        for r in csv.DictReader(f):
            y, x = int(r["gridY"]), int(r["gridX"])
            cells[(y, x)] = r
            # cheap prefilter before the exact distance
            if abs(float(r["lat"]) - lat) < 0.2 and abs(float(r["lon"]) - lon) < 0.3:
                d = meters(lat, lon, float(r["lat"]), float(r["lon"]))
                if best is None or d < best[0]:
                    best = (d, y, x)
    if best is None:
        return None
    d, y, x = best
    land = sum((y + dy, x + dx) not in cells for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dy or dx)
    r = cells[(y, x)]
    return {"gridY": y, "gridX": x, "lat": float(r["lat"]), "lon": float(r["lon"]),
            "depth_m": float(r["depth_m"]) if r["depth_m"] else None,
            "distance_m": round(d), "land_neighbors": land}


def assess(cell, max_m):
    """Return (usable, notes) for how well this cell represents the requested point."""
    notes = []
    if cell["distance_m"] > max_m:
        return False, [f"Nearest model water cell is {cell['distance_m']} m away (limit {max_m} m). "
                       "The model does not resolve water this close to the point; don't use it here."]
    if cell["distance_m"] > GOOD_M:
        notes.append(f"Nearest water cell is {cell['distance_m']} m away, more than one ~{CELL_M} m cell. "
                     "Treat values as the nearby open water, not the launch itself.")
    if cell["land_neighbors"] >= 3:
        notes.append(f"Cell borders land on {cell['land_neighbors']} of 8 sides. The model is least reliable "
                     "next to shore, and coves and eddies smaller than ~500 m are not resolved.")
    return True, notes


def fetch(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": "kayak-trip-planner"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode()


def coverage_end():
    for line in fetch(f"{ERDDAP}.das").splitlines():
        if "time_coverage_end" in line:
            return dt.datetime.fromisoformat(line.split('"')[1].replace("Z", "+00:00"))
    raise RuntimeError("time_coverage_end not found")


def iso(t):
    return t.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def data_url(cell, start, end):
    sel = f"[({iso(start)}):1:({iso(end)})][({cell['gridY']})][({cell['gridX']})]"
    return f"{ERDDAP}.csv?VelEast5{sel},VelNorth5{sel}"


def parse(text, tz):
    out = []
    for row in list(csv.reader(text.splitlines()))[2:]:
        if row[3] in ("NaN", "") or row[4] in ("NaN", ""):
            continue
        e, n = float(row[3]), float(row[4])
        deg = (math.degrees(math.atan2(e, n)) + 360) % 360
        t = dt.datetime.fromisoformat(row[0].replace("Z", "+00:00")).astimezone(tz)
        out.append({"time": t.isoformat(timespec="minutes"), "speed_kt": round(math.hypot(e, n) * 1.944, 2),
                    "toward_deg": round(deg), "toward": COMPASS[int((deg + 11.25) // 22.5) % 16]})
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--lat", type=float, required=True)
    ap.add_argument("--lon", type=float, required=True, help="negative for west")
    ap.add_argument("--date", required=True, help="local date YYYY-MM-DD")
    ap.add_argument("--start", default="08:00", help="local start time HH:MM (default 08:00)")
    ap.add_argument("--hours", type=float, default=10, help="window length in hours (default 10)")
    ap.add_argument("--tz", default="America/Los_Angeles", help="IANA time zone (default America/Los_Angeles)")
    ap.add_argument("--max-dist-m", type=int, default=1000,
                    help="reject the nearest water cell if farther than this (default 1000)")
    ap.add_argument("--url-only", action="store_true", help="print checks and URLs, don't fetch")
    ap.add_argument("--json", action="store_true", help="print JSON")
    args = ap.parse_args()

    if not GRID_FILE.exists():
        sys.exit(f"Missing {GRID_FILE}. Run build_salishsea_grid.py.")
    tz = ZoneInfo(args.tz)
    start = dt.datetime.combine(dt.date.fromisoformat(args.date), dt.time.fromisoformat(args.start), tz)
    end = start + dt.timedelta(hours=args.hours)

    result = {"source": "SalishSeaCast (UBC), near-surface depth-averaged currents, hourly averages (times are mid-hour)", "dataset": ERDDAP + ".html",
              "point": {"lat": args.lat, "lon": args.lon}, "window": [start.isoformat(), end.isoformat()]}
    cell = nearest_cell(args.lat, args.lon)
    if cell is None:
        result.update(usable=False, notes=["Point is outside the SalishSeaCast domain."])
        return report(result, args.json, 2)
    usable, notes = assess(cell, args.max_dist_m)
    result.update(cell=cell, usable=usable, notes=notes)
    if not usable:
        return report(result, args.json, 2)

    if args.url_only:
        result["coverage_url"] = ERDDAP + ".das (read time_coverage_end first)"
        result["data_url"] = data_url(cell, start, end)
        result["notes"].append("Convert: speed kt = sqrt(E^2+N^2) x 1.944; toward = atan2(E, N) deg from north. Times are UTC.")
        return report(result, args.json, 0)

    try:
        horizon = coverage_end()
    except Exception as e:  # network or format failure
        result["notes"].append(f"Could not reach SalishSeaCast: {e}")
        return report(result, args.json, 1)
    result["forecast_ends"] = horizon.astimezone(tz).isoformat(timespec="minutes")
    if start > horizon:
        result["notes"].append("Trip window is past the end of the forecast. Re-check closer to the day.")
        return report(result, args.json, 3)
    if end > horizon:
        result["notes"].append("Forecast ends partway through the window; later hours are not covered.")
        end = horizon
    result["data_url"] = data_url(cell, start, end)
    try:
        result["hours"] = parse(fetch(result["data_url"]), tz)
    except Exception as e:
        result["notes"].append(f"Data request failed: {e}")
        return report(result, args.json, 1)
    if result["hours"]:
        peak = max(result["hours"], key=lambda h: h["speed_kt"])
        result["peak"] = peak
    return report(result, args.json, 0)


def report(r, as_json, code):
    if as_json:
        print(json.dumps(r, indent=2))
    else:
        print(f"SalishSeaCast modeled currents near {r['point']['lat']}, {r['point']['lon']}")
        if "cell" in r:
            c = r["cell"]
            depth = f", depth {c['depth_m']:.0f} m" if c["depth_m"] is not None else ""
            print(f"  Model cell ({c['gridY']}, {c['gridX']}) at {c['lat']:.4f}, {c['lon']:.4f}: "
                  f"{c['distance_m']} m from the point{depth}, land on {c['land_neighbors']}/8 sides")
        print(f"  Usable here: {'yes' if r['usable'] else 'NO'}")
        if "forecast_ends" in r:
            print(f"  Forecast runs to {r['forecast_ends']}")
        for h in r.get("hours", []):
            print(f"  {h['time'][:16].replace('T', ' ')}  {h['speed_kt']:.2f} kt toward {h['toward']}")
        if r.get("hours"):
            print("  (hourly averages; each time is the middle of its hour)")
        if "peak" in r:
            print(f"  Peak in window: {r['peak']['speed_kt']:.2f} kt toward {r['peak']['toward']} at {r['peak']['time'][11:16]}")
        for k in ("coverage_url", "data_url"):
            if k in r:
                print(f"  {k}: {r[k]}")
        for n in r["notes"]:
            print(f"  Note: {n}")
    sys.exit(code)


if __name__ == "__main__":
    main()
