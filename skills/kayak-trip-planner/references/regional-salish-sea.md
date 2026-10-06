# Regional extras: Salish Sea (Puget Sound, San Juan Islands, Bellingham Bay, Strait of Juan de Fuca, Strait of Georgia)

Use when the launch point is roughly between 47.0 and 50.5 N and 122.0 and 125.0 W. These add detail; the national NOAA/NWS sources still come first.

## Modeled surface currents: which source
Two models give hourly currents at a point. Both run a few hours to days ahead, so use them in the weather-narrowing and final-check stages.

1. **NOAA SSCOFS first** (`scripts/sscofs_currents.py`): NOAA's operational model, ~50-150 m mesh in passes and bays, ~72 h ahead. Also covers the Columbia River and the WA/OR outer coast.
2. **SalishSeaCast as a cross-check or fallback** (`scripts/salishsea_currents.py`, below): ~500 m research model, ~36-48 h ahead; the model behind OceanConnect. Coarser, so it fails the close-enough check in narrow passes.

Both scripts take the same arguments, do the same close-enough check (nearest model water within 1 km, flags beyond 400 m and next to shore), and return hourly speed and the direction the water flows toward, in local time. Use the on-water point from Step 2. If both pass and disagree a lot, say so and lean on the NOAA station predictions.

**Models vs. NOAA current predictions.** Where a NOAA prediction station sits right on the route, its slack times and peak speeds come first. Tested at Deception Pass, SSCOFS got the flood/slack/ebb timing within ~20-30 min but peak speeds ~30-50% low (3.9 vs 5.5 kt flood). Models are most valuable away from stations, in bays and along shorelines where a distant channel station's speeds would mislead.

### NOAA SSCOFS
```
python3 scripts/sscofs_currents.py --lat LAT --lon LON --date YYYY-MM-DD --start HH:MM --hours N
```
Also returns modeled surface water temperature per hour (often the only water temperature available near shore). Uses the bundled mesh index `data/sscofs_mesh.csv.gz` (offline), then one ~400-byte request per hour to NOAA's THREDDS server, from the newest model run (03, 09, 15, 21 UTC) that covers it. Flags hours when the element is dry (tidal flat). Exit codes as below. With no shell internet, `--url-only` prints the checks and a per-hour URL template; the brackets must stay percent-encoded (`%5B`, `%5D`) or the server returns 400. Info: https://tidesandcurrents.noaa.gov/ofs/sscofs/sscofs.html

## Modeled surface currents: SalishSeaCast (UBC)
A ~500 m research model of the whole Salish Sea; the model behind the OceanConnect app. Hourly, and runs only ~36-48 h ahead.

Run:
```
python3 scripts/salishsea_currents.py --lat LAT --lon LON --date YYYY-MM-DD --start HH:MM --hours N
```
Use the on-water point from Step 2, not the launch on shore. The script finds the nearest model water cell from the bundled `data/salishsea_grid.csv.gz` (offline), checks it, reads the forecast horizon, and returns hourly speed (kt) and the direction the water flows toward, in local time.

**Close-enough check (the script does this; report it in the plan):**
- Nearest water cell more than 1 km from the point: **not usable**, exit code 2. The model doesn't resolve water there (small coves, narrow passes like Deception Pass, lakes). Fall back to NOAA current stations and say the model was checked and didn't apply.
- 400 m-1 km: usable, but describes the nearby open water, not the launch. Say so.
- Cell bordering land on 3+ sides: nearshore, least reliable. Say so.
- Exit code 3: trip window past the forecast; list as out of range and give a re-check time.

If the shell has no internet, add `--url-only`: it still does the cell checks offline and prints the data URL to fetch with the web-fetch tool (check `time_coverage_end` in the `.das` first). Convert: speed kt = sqrt(E^2 + N^2) x 1.944; toward = atan2(E, N) degrees from north; times are UTC.

Limits: research model, not an official forecast; eddies smaller than ~500 m are not resolved; values are near-surface averages. Use it to judge how strong current is and which way it sets near the route, alongside (not instead of) NOAA predictions for slack timing.

## Visual check: OceanConnect
https://oceanconnect.ca (Hakai Institute) maps modeled currents, wind, waves and webcams for BC and Washington. It renders in JavaScript, so the fetch tool can't read it. Recommend it to the paddler for a morning-of look, especially the webcams for fog.

## Local notes
- Bellingham Bay / Chuckanut Bay: currents in the bay are weak; wind is the main factor. NOAA's closest current station, PCT2116 off Eliza Island (~3.5 mi W), is rated weak and variable and has no predictions. The nearest stations with predictions are PUG1707 Sinclair Island (~7.7 mi W; flood NW, ebb SE, about 1 kt) and PUG1741 Bellingham Channel North (~8.8 mi WSW; flood N, ebb SW, 2.5-3 kt in the channel). Use them for slack timing only; their directions and speeds describe those channels, not the bay.
- Fall and winter fog often sits on Bellingham Bay and Puget Sound into late morning.
