#!/usr/bin/env python3
"""Modeled surface currents and water temperature at a point from NOAA SSCOFS (Salish Sea and Columbia River OFS).

Finds the nearest model element from the bundled mesh index in ../data (offline),
checks it is close enough to mean something, then fetches one tiny OPeNDAP slice
(~350 bytes) per forecast hour from the NOAA CO-OPS THREDDS server.

    python3 sscofs_currents.py --lat 48.406 --lon -122.645 --date 2026-10-06
    python3 sscofs_currents.py --lat 48.406 --lon -122.645 --date 2026-10-06 --start 10:00 --hours 4 --json
    python3 sscofs_currents.py --lat 48.406 --lon -122.645 --date 2026-10-06 --url-only

--url-only prints the element checks and the per-hour URLs without fetching, for
environments where the shell has no internet but a web-fetch tool does.

Exit codes: 0 ok, 1 data unavailable, 2 no usable element (outside the model or too far),
3 trip window past the forecast.
"""
import argparse
import csv
import datetime as dt
import gzip
import json
import math
import pathlib
import re
import sys
import urllib.request
from zoneinfo import ZoneInfo

THREDDS = "https://opendap.co-ops.nos.noaa.gov/thredds"
MESH_FILE = pathlib.Path(__file__).resolve().parent.parent / "data" / "sscofs_mesh.csv.gz"
COMPASS = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
CYCLES = (3, 9, 15, 21)  # UTC run hours, 4 per day
MAX_LEAD = 72  # forecast hours per run
GOOD_M = 400  # nearest element center farther than this: describes nearby water, not the point
COARSE_M = 500  # local mesh spacing above this: features smaller than the spacing are not resolved


def meters(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lon2 - lon1) / 2) ** 2
    return 6371000 * 2 * math.asin(math.sqrt(a))


def nearest_element(lat, lon):
    near = []  # (distance, index, row) for elements in a box around the point
    with gzip.open(MESH_FILE, "rt") as f:
        for i, r in enumerate(csv.DictReader(f)):
            la, lo = float(r["lat"]), float(r["lon"])
            if abs(la - lat) < 0.1 and abs(lo - lon) < 0.15:
                near.append((meters(lat, lon, la, lo), i, r))
    if not near:
        return None
    near.sort(key=lambda t: t[0])
    d, i, r = near[0]
    la, lo = float(r["lat"]), float(r["lon"])
    # Local resolution: distance from this element to its nearest neighbouring element center.
    spacing = min((meters(la, lo, float(o["lat"]), float(o["lon"])) for _, j, o in near[1:60] if j != i), default=None)
    return {"element": i, "lat": la, "lon": lo, "depth_m": float(r["depth_m"]), "distance_m": round(d),
            "mesh_spacing_m": round(spacing) if spacing is not None else None,
            "shore_sides": int(r["shore_sides"]), "elements_within_1km": sum(1 for t in near if t[0] <= 1000)}


def assess(el, max_m):
    """Return (usable, notes) for how well this element represents the requested point."""
    notes = []
    if el["distance_m"] > max_m:
        return False, [f"Nearest model element is {el['distance_m']} m away (limit {max_m} m). "
                       "The model does not resolve water this close to the point; don't use it here."]
    if el["distance_m"] > GOOD_M:
        notes.append(f"Nearest element is {el['distance_m']} m away. Treat values as the nearby water, not the point itself.")
    if el["mesh_spacing_m"] and el["mesh_spacing_m"] > COARSE_M:
        notes.append(f"Mesh spacing here is ~{el['mesh_spacing_m']} m; features smaller than that are not resolved.")
    if el["shore_sides"]:
        notes.append("Element touches the model shoreline; nearshore values are the least reliable.")
    return True, notes


def fetch(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": "kayak-trip-planner"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode()


def file_path(cycle, lead):
    return (f"NOAA/SSCOFS/MODELS/{cycle:%Y/%m/%d}/"
            f"sscofs.t{cycle:%H}z.{cycle:%Y%m%d}.fields.f{lead:03d}.nc")


def data_url(cycle, lead, e):
    sl = f"%5B0:0%5D%5B0:0%5D%5B{e}:{e}%5D"  # [0:0][0:0][e:e]; brackets must be encoded
    return (f"{THREDDS}/dodsC/{file_path(cycle, lead)}.ascii?"
            f"time,u{sl},v{sl},temp{sl},wet_cells%5B0:0%5D%5B{e}:{e}%5D")


_catalogs = {}


def available(cycle):
    """Set of forecast leads published for this run (cached per day)."""
    day = cycle.date()
    if day not in _catalogs:
        try:
            xml = fetch(f"{THREDDS}/catalog/NOAA/SSCOFS/MODELS/{day:%Y/%m/%d}/catalog.xml")
        except Exception:
            xml = ""
        _catalogs[day] = set(re.findall(r'sscofs\.t(\d\d)z\.\d{8}\.fields\.f(\d{3})\.nc', xml))
    return {int(f) for h, f in _catalogs[day] if int(h) == cycle.hour}


def recent_cycles(now, days=3):
    t = now.replace(minute=0, second=0, microsecond=0)
    out = []
    for back in range(days * 24 + 1):
        c = t - dt.timedelta(hours=back)
        if c.hour in CYCLES:
            out.append(c)
    return out  # newest first


def plan_requests(start, end, now):
    """Pick, for each whole UTC hour in the window, the newest published run that covers it.

    Returns (requests, latest_run, horizon); requests is a list of (valid_time, cycle, lead)."""
    runs = [(c, available(c)) for c in recent_cycles(now)]
    runs = [(c, leads) for c, leads in runs if leads]
    if not runs:
        return [], None, None
    latest, latest_leads = runs[0]
    horizon = latest + dt.timedelta(hours=max(latest_leads))
    t = start.astimezone(dt.timezone.utc)
    t = t.replace(minute=0, second=0, microsecond=0) + (dt.timedelta(hours=1) if t.minute or t.second else dt.timedelta())
    reqs = []
    while t <= end:
        for c, leads in runs:
            lead = int((t - c).total_seconds() // 3600)
            if 0 <= lead <= MAX_LEAD and lead in leads:
                reqs.append((t, c, lead))
                break
        t += dt.timedelta(hours=1)
    return reqs, latest, horizon


def parse(text):
    """Return (u, v, temp_c, wet) from an OPeNDAP ASCII reply for one element and hour."""
    vals = {}
    cur = None
    for line in text.split("-" * 45, 1)[1].splitlines():
        line = line.strip()
        m = re.match(r"^(\w+)\[", line)
        if m and line.endswith("]"):
            cur = m.group(1)
        elif cur and line:
            vals[cur] = float(line.rsplit(",", 1)[-1])
            cur = None
    return vals["u"], vals["v"], vals.get("temp"), int(vals.get("wet_cells", 1))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--lat", type=float, required=True)
    ap.add_argument("--lon", type=float, required=True, help="negative for west")
    ap.add_argument("--date", required=True, help="local date YYYY-MM-DD")
    ap.add_argument("--start", default="08:00", help="local start time HH:MM (default 08:00)")
    ap.add_argument("--hours", type=float, default=10, help="window length in hours (default 10)")
    ap.add_argument("--tz", default="America/Los_Angeles", help="IANA time zone (default America/Los_Angeles)")
    ap.add_argument("--max-dist-m", type=int, default=1000,
                    help="reject the nearest element if farther than this (default 1000)")
    ap.add_argument("--url-only", action="store_true", help="print checks and URLs, don't fetch")
    ap.add_argument("--json", action="store_true", help="print JSON")
    args = ap.parse_args()

    if not MESH_FILE.exists():
        sys.exit(f"Missing {MESH_FILE}. Run build_sscofs_mesh.py.")
    tz = ZoneInfo(args.tz)
    start = dt.datetime.combine(dt.date.fromisoformat(args.date), dt.time.fromisoformat(args.start), tz)
    end = start + dt.timedelta(hours=args.hours)

    result = {"source": "NOAA SSCOFS (FVCOM), surface layer currents and water temperature, hourly; forecast guidance",
              "info": "https://tidesandcurrents.noaa.gov/ofs/sscofs/sscofs.html",
              "point": {"lat": args.lat, "lon": args.lon}, "window": [start.isoformat(), end.isoformat()]}
    el = nearest_element(args.lat, args.lon)
    if el is None:
        result.update(usable=False, notes=["Point is outside the SSCOFS domain (Salish Sea, Columbia River, WA/OR coast)."])
        return report(result, args.json, 2)
    usable, notes = assess(el, args.max_dist_m)
    result.update(element=el, usable=usable, notes=notes)
    if not usable:
        return report(result, args.json, 2)

    now = dt.datetime.now(dt.timezone.utc)
    if args.url_only:
        result["notes"].append(
            "Each model run (03, 09, 15, 21 UTC) publishes fields.fNNN files valid NNN hours after the run, to f072. "
            "Use the newest run that covers each hour; the newest run may still be filling in. "
            "Speed kt = sqrt(u^2+v^2) x 1.944 (u east, v north, m/s); toward = atan2(u, v) deg from north; "
            "temp is surface water temperature in deg C; wet_cells 0 = dry (tidal flat).")
        result["url_template"] = data_url(dt.datetime(2000, 1, 1, 15), 1, el["element"]).replace(
            "2000/01/01", "YYYY/MM/DD").replace("t15z.20000101", "tHHz.YYYYMMDD").replace("f001", "fNNN")
        return report(result, args.json, 0)

    reqs, latest, horizon = plan_requests(start, end, now)
    if latest is None:
        result["notes"].append("Could not list SSCOFS runs on the NOAA THREDDS server.")
        return report(result, args.json, 1)
    result["model_run"] = f"{latest:%Y-%m-%d %H}z"
    result["forecast_ends"] = horizon.astimezone(tz).isoformat(timespec="minutes")
    if start > horizon:
        result["notes"].append("Trip window is past the end of the forecast. Re-check closer to the day.")
        return report(result, args.json, 3)
    if end > horizon:
        result["notes"].append("Forecast ends partway through the window; later hours are not covered.")
    hours, failed = [], 0
    for t, c, lead in reqs:
        try:
            u, v, temp, wet = parse(fetch(data_url(c, lead, el["element"])))
        except Exception:
            failed += 1
            continue
        deg = (math.degrees(math.atan2(u, v)) + 360) % 360
        hours.append({"time": t.astimezone(tz).isoformat(timespec="minutes"), "run": f"{c:%Y-%m-%d %H}z f{lead:03d}",
                      "speed_kt": round(math.hypot(u, v) * 1.944, 2), "toward_deg": round(deg),
                      "toward": COMPASS[int((deg + 11.25) // 22.5) % 16],
                      "water_temp_f": round(temp * 9 / 5 + 32) if temp is not None else None, "dry": not wet})
    if failed:
        result["notes"].append(f"{failed} hourly request(s) failed and are missing.")
    if any(h["dry"] for h in hours):
        result["notes"].append("Element is dry (tidal flat) for part of the window.")
    result["hours"] = hours
    if hours:
        result["peak"] = max(hours, key=lambda h: h["speed_kt"])
    return report(result, args.json, 0 if hours else 1)


def report(r, as_json, code):
    if as_json:
        print(json.dumps(r, indent=2))
    else:
        print(f"NOAA SSCOFS modeled currents near {r['point']['lat']}, {r['point']['lon']}")
        if "element" in r:
            e = r["element"]
            print(f"  Element {e['element']} at {e['lat']:.4f}, {e['lon']:.4f}: {e['distance_m']} m from the point, "
                  f"depth {e['depth_m']:.0f} m, mesh spacing ~{e['mesh_spacing_m']} m, "
                  f"{e['elements_within_1km']} elements within 1 km")
        print(f"  Usable here: {'yes' if r['usable'] else 'NO'}")
        if "model_run" in r:
            print(f"  Latest run {r['model_run']}; forecast runs to {r['forecast_ends']}")
        for h in r.get("hours", []):
            dry = "  (dry)" if h["dry"] else ""
            wt = f"  water {h['water_temp_f']} F" if h["water_temp_f"] is not None else ""
            print(f"  {h['time'][:16].replace('T', ' ')}  {h['speed_kt']:.2f} kt toward {h['toward']}{wt}{dry}")
        if "peak" in r:
            print(f"  Peak in window: {r['peak']['speed_kt']:.2f} kt toward {r['peak']['toward']} at {r['peak']['time'][11:16]}")
        if "url_template" in r:
            print(f"  url_template: {r['url_template']}")
        for n in r["notes"]:
            print(f"  Note: {n}")
    sys.exit(code)


if __name__ == "__main__":
    main()
