#!/usr/bin/env python3
"""Sunrise and sunset (local time) for a date and place. Offline; NOAA solar equations, ~1-2 min accuracy.

    python3 sun_times.py --lat 48.66 --lon -122.49 --date 2026-10-08 --tz America/Los_Angeles
"""
import argparse
import datetime as dt
import math
from zoneinfo import ZoneInfo


def sun_events(lat, lon, date):
    """Return (sunrise_utc, sunset_utc) datetimes, or None for polar day/night."""
    n = date.timetuple().tm_yday
    g = 2 * math.pi / 365 * (n - 1 + 0.5)
    eqtime = 229.18 * (0.000075 + 0.001868 * math.cos(g) - 0.032077 * math.sin(g)
                       - 0.014615 * math.cos(2 * g) - 0.040849 * math.sin(2 * g))
    decl = (0.006918 - 0.399912 * math.cos(g) + 0.070257 * math.sin(g) - 0.006758 * math.cos(2 * g)
            + 0.000907 * math.sin(2 * g) - 0.002697 * math.cos(3 * g) + 0.00148 * math.sin(3 * g))
    cos_ha = (math.cos(math.radians(90.833)) / (math.cos(math.radians(lat)) * math.cos(decl))
              - math.tan(math.radians(lat)) * math.tan(decl))
    if not -1 <= cos_ha <= 1:
        return None
    ha = math.degrees(math.acos(cos_ha))
    midnight = dt.datetime(date.year, date.month, date.day, tzinfo=dt.timezone.utc)
    rise = midnight + dt.timedelta(minutes=720 - 4 * (lon + ha) - eqtime)
    set_ = midnight + dt.timedelta(minutes=720 - 4 * (lon - ha) - eqtime)
    return rise, set_


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--lat", type=float, required=True)
    ap.add_argument("--lon", type=float, required=True, help="negative for west")
    ap.add_argument("--date", required=True, help="YYYY-MM-DD")
    ap.add_argument("--tz", required=True, help="IANA time zone, e.g. America/New_York")
    args = ap.parse_args()
    date = dt.date.fromisoformat(args.date)
    ev = sun_events(args.lat, args.lon, date)
    if ev is None:
        print("No sunrise/sunset on this date (polar day or night).")
        return
    tz = ZoneInfo(args.tz)
    rise, set_ = (t.astimezone(tz) for t in ev)
    print(f"Sunrise {rise:%H:%M %Z}  Sunset {set_:%H:%M %Z}  ({args.date}, {args.lat}, {args.lon})")


if __name__ == "__main__":
    main()
