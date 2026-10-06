---
name: kayak-trip-planner
description: Use when someone asks about a good day or time to sea kayak in US waters, or wants tides, tidal currents, wind, waves and weather checked for a paddle route or launch site.
---

# Kayak trip planner (US waters)

Sea kayaking needs more prep than a run or bike ride: tide, current, wind, waves, fog and daylight all have to line up. This skill pulls public NOAA and NWS data for a launch point, checks each go/no-go factor against the paddler's profile, recommends the best day, launch time and route direction, and states plainly what the plan rests on and what it does not cover.

Plans may be shared with people who never saw the conversation, so every plan must stand on its own. This skill gives planning information only; the paddler makes the go/no-go call.

Coverage: US coastal waters, estuaries and the Great Lakes (NOAA/NWS sources). Outside the US, say the data sources don't cover it and stop. On inland lakes and rivers there are no tide or marine forecasts; use the land forecast and say so.

## Step 0: Required acceptance of terms (before the first plan in every conversation)

Before giving any plan, recommendation, go/no-go verdict or route in a conversation, show this notice exactly, and ask the person to reply "I accept". Gathering their trip details (Step 1) can happen alongside it, but no plan is given until they accept.

> **Safety notice and terms of use.** Kayak Trip Planner gives general planning information from public NOAA and NWS data, which can be wrong, late, incomplete or unavailable. It does not observe real conditions, know your abilities or know local hazards, and it is not professional advice, instruction or a guarantee of safety. Paddling is dangerous and can cause injury or death. You are solely responsible for deciding whether, when and where to paddle, and for your own safety and that of anyone with you. By using this tool you accept all risks of using it, release its authors and contributors from all liability, and agree to hold them harmless from any claims, losses or damages arising from your use of it or reliance on it. Full terms: TERMS.md in this skill's repository.
>
> Reply **"I accept"** to continue.

- Accept only a clear acceptance ("I accept", "I agree", "yes, I accept"). If the reply is ambiguous, ask once more.
- If they decline, don't give plans, verdicts or routes. You can still explain general concepts (what slack water is, how to read a tide table) and point them to the sources in Step 4.
- Ask once per conversation. If they already accepted earlier in the conversation, don't ask again.
- When a plan is shared, it already carries its own "Not covered by this plan" section; don't repeat the full notice in every plan.

## Files in this skill

- `scripts/nearest_stations.py` finds the nearest NOAA tide stations, current stations and NDBC buoys to a lat/lon, from the bundled snapshot in `data/`. Runs offline.
- `scripts/sun_times.py` gives sunrise and sunset for a date and place. Runs offline.
- `scripts/build_station_data.py` rebuilds `data/` from NOAA. Needs internet; maintainers run it, not part of planning.
- `references/regional-*.md` hold optional extras for specific regions. Read one only if the launch point is inside its area.

Run scripts with `python3 <skill-dir>/scripts/<name>.py --help` for options.

## Step 1: Paddler profile

Use a profile the person has already given (earlier in the conversation or in memory). Otherwise ask once, in one short message, offering these defaults:

- Cruising speed: 2.5 mph (~2.2 kt) for touring kayaks; 2 mph for recreational boats or relaxed groups
- Trip length: 3 hours
- Launch window: when they'd like to start
- Skill level: beginner, intermediate or advanced (sets the thresholds in Step 4)
- Cold-water gear: dry suit, wet suit, or none

If the trip is soon and the person seems to want an answer now, proceed with the defaults and say which were assumed. Restate the profile used in every plan. Don't lecture about gear they already have.

## Step 2: Locate the launch and the stations

1. Get the launch point(s) as lat/lon. If the person gives a place name, use known coordinates or a quick web search, and state the coordinates you used.
2. Pick a point ON THE WATER, about 0.5 mi offshore from the launch, for marine forecasts.
3. Run `python3 scripts/nearest_stations.py --lat LAT --lon LON --kind all`. It lists the nearest tide stations, current stations and buoys with distances and bearings.
   - Prefer the nearest tide station; note its distance. Over ~10 mi, or across a headland or into a different basin, flag that times may differ.
   - Current stations are often in channels miles away. Use a distant one for the TIMING and DIRECTION of slack, flood and ebb, never its speeds; channel speeds can be several times what's in a nearby bay. Say this in the plan.
   - Weak-and-variable current stations (NOAA type W) have no predictions; the API returns "Currents predictions are not available". The script skips them and lists any closer than the usable stations in a note. Don't fetch them. A nearby one is still useful: say in the plan that NOAA rates currents near the launch as weak and variable.
   - If the bundled data is missing, ask the person for station IDs from https://tidesandcurrents.noaa.gov/noaacurrents/ and https://tidesandcurrents.noaa.gov/tide_predictions.html, and verify each with https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations/ID.json. Never guess an ID.

## Step 3: Decide the planning stage

Never present data past its horizon as a forecast.

| Stage | Trip is | Can check | Can't check yet |
|---|---|---|---|
| Tide shortlist | More than 7 days out | Tides, current-station predictions, daylight | Wind, waves, fog, rain |
| Weather narrowing | 2-7 days out | All above + NWS marine forecast (solid to ~3 days, rough beyond) | Real-time observations |
| Final check | Today or tomorrow | All above + buoy observations, any regional models | - |

In the tide-shortlist stage, rank days by tide fit and say when to re-check (about 3 days out and the day before).

## Step 4: Pull the data

Fetch with the web-fetch tool. Record each source's URL, issue/update time and the period covered; these go in the plan. If the shell has internet access, `curl` works too; in many environments it doesn't, so don't depend on it.

### Tides (NOAA CO-OPS; horizon: months to years)
```
https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?begin_date=YYYYMMDD&end_date=YYYYMMDD&station=ID&product=predictions&datum=MLLW&time_zone=lst_ldt&interval=hilo&units=english&format=json
```
Predictions are astronomical; wind and air pressure can shift real water levels by a few tenths of a foot or more. Great Lakes have no meaningful tide; skip this and watch wind-driven water level changes instead.

### Tidal currents (NOAA CO-OPS; horizon: months to years)
```
https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?begin_date=YYYYMMDD&end_date=YYYYMMDD&station=ID&product=currents_predictions&interval=MAX_SLACK&time_zone=lst_ldt&units=english&format=json
```
Add `&bin=N` with the bin from `nearest_stations.py` (the shallowest bin, closest to what a kayak feels). Returns slack, max flood and max ebb times, speeds in knots (ebb negative) and mean flood/ebb directions.

### Wind, waves, fog, rain (NWS marine point forecast; horizon: ~5-7 days)
```
https://forecast.weather.gov/MapClick.php?lat=LAT&lon=LON&unit=0&lg=english&FcstType=text&TextType=1
```
- Use the on-water point. This returns the marine point forecast, with any Small Craft Advisory, Gale Warning or Dense Fog Advisory listed at the top.
- ALWAYS check the "Last Update" time. This site sometimes serves a stale cached page that is weeks old, especially for land points or the `FcstType=digital` view. Discard anything not issued in the last ~24 h and list it as unavailable.
- Marine forecasts cover broad zones in 5 kt steps. Local gusts, gap winds and afternoon sea breezes can exceed them; say so.

### Real-time observations (NDBC; final-check stage only)
```
https://www.ndbc.noaa.gov/data/realtime2/BUOYID.txt
```
Latest rows first: wind speed and gusts (m/s), wave height (m), water temperature (deg C). Convert units before reporting. Note the buoy's distance and exposure; an offshore buoy overstates conditions in a sheltered bay.

### Daylight
Run `python3 scripts/sun_times.py --lat LAT --lon LON --date YYYY-MM-DD --tz IANA_ZONE`. Flag trips ending within an hour of sunset.

### Regional extras
If a `references/regional-*.md` file covers the launch area, read it and use its sources. These add detail (for example, modeled currents for the Salish Sea) but don't replace the national sources.

### Access notes
- The web-fetch tool summarizes long pages and truncates large files. Don't fetch NOAA's full station lists; that's what the bundled data is for.
- `api.weather.gov` blocks some automated fetchers. If it fails, use the forecast.weather.gov URL above and don't retry.
- Some map sites (OceanConnect, Windy) render in JavaScript and return nothing to the fetch tool. Recommend them for a visual check; never claim to have read them.

## Step 5: Evaluate each candidate day

Default thresholds by skill level. Say which set was used, and let the person override.

| Factor | Beginner | Intermediate | Advanced |
|---|---|---|---|
| Sustained wind, go | <=8 kt | <=12 kt | <=15 kt |
| Sustained wind, no-go | >10 kt or any advisory | >15 kt or Small Craft Advisory | >20 kt or Gale Warning |
| Waves, no-go | >1 ft | >2 ft | >3 ft |
| Current against you on the return leg, no-go | >0.5 kt | >1 kt | > half the paddling speed |
| Fog | No-go with any fog in the window | No-go with Dense Fog Advisory | Caution with Dense Fog Advisory |
| Water temp below 60 F with no immersion gear | No-go | Stay near shore | Stay near shore |
| Thunder or lightning in the forecast | No-go | No-go | No-go |

Also check:
- **Wind against current** stacks up steep, short waves even at moderate speeds. Treat it one level more conservatively.
- **Launch at low tide**: mudflats, long carries, exposed rocks. A rising tide during the trip is safer; a falling one can strand boats in shallow bays.
- **Afternoon sea breeze**: often builds after midday on warm days. Prefer heading upwind first.
- **Offshore wind** (blowing from land to water) is the riskiest direction for a tired paddler. Flag it.

## Step 6: Plan the route

- Do the outbound leg against the weaker push (current or wind) so the return is assisted. Use slack times and the flood/ebb directions to choose.
- Time features to the tide: rocks and tidepools near low water, shallow bays and marshes near high water.
- Distance = speed x duration, minus ~20% for breaks and margin. Give rough clock times for the turnaround and key stops.
- Prefer routes that keep a landing within reach. Mention crossings of shipping lanes or ferry routes if the route has them.

## Step 7: Write the plan

Lead with the recommendation (best day and a backup) and the planning stage. Then:
- A compact table per candidate day: low/high times and heights, slack and max current times, wind, waves, sky, fog, verdict.
- Launch time, route and direction, with the reason.
- When to re-check, if the trip is beyond the reliable forecast range.

Then ALWAYS end with this section, filled in, even when everything looks good:

### What this plan is based on
- **Paddler assumptions:** speed, duration, skill level and the thresholds used, gear.
- **Sources checked:** each source with its issue/update time and the period covered (link each); each station's distance from the launch; for current stations, that speeds apply at that station only.
- **Reliability at this lead time:** which parts are predictions (tides, currents) and which are forecasts (weather), and how reliable each is now.
- **Not checked or unavailable:** anything that failed, was stale or was out of range.
- **Not covered by this plan:** local hazards (rocks, surf, rebound off cliffs, boat and ferry traffic, shipping lanes), closures and permits, launch access, and real-time conditions on the day. Look at the water before launching and make your own go/no-go call. Conditions change; this plan is not a guarantee of safety.
