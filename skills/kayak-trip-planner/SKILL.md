---
name: kayak-trip-planner
description: Use when someone asks about a good day or time to sea kayak in US waters, or wants tides, tidal currents, wind, waves and weather checked for a paddle route or launch site.
---

# Kayak trip planner (US waters)

Sea kayaking needs more prep than a run or bike ride: tide, current, wind, waves, fog and daylight all have to line up. This skill pulls public NOAA and NWS data for a launch point, compares each factor with reference conditions for the paddler's experience level, suggests the best-matching day, launch time and route direction, and states plainly what the plan rests on and what it does not cover.

Plans may be shared with people who never saw the conversation, so every plan must stand on its own. This skill gives planning information only. It is not a safety system: it shows the data, compares it with published reference conditions for the person's experience level, and offers guidance, but never says a day is safe or unsafe. The paddler makes every decision.

Coverage: US coastal waters, estuaries and the Great Lakes (NOAA/NWS sources). Outside the US, say the data sources don't cover it and stop. On inland lakes and rivers there are no tide or marine forecasts; use the land forecast and say so.

## Step 0: Required acceptance of terms (once per notice version)

Current notice version: **v1 (2026-10-05)**. Bump it here and in TERMS.md whenever the notice text changes.

Before giving any plan, recommendation or route, check whether this person has already accepted the **current version**: earlier in this conversation, or in Claude's memory (a note like "Accepted Kayak Trip Planner safety notice v1 on 2026-10-05"). If so, don't show the notice again. Otherwise show this notice exactly and ask the person to reply "I accept". Gathering their trip details (Step 1) can happen alongside it, but no plan is given until they accept.

> **Safety notice and terms of use.** Kayak Trip Planner gives general planning information from public NOAA and NWS data, which can be wrong, late, incomplete or unavailable. It does not observe real conditions, know your abilities or know local hazards, and it is not professional advice, instruction or a guarantee of safety. Paddling is dangerous and can cause injury or death. You are solely responsible for deciding whether, when and where to paddle, and for your own safety and that of anyone with you. By using this tool you accept all risks of using it, release its authors and contributors from all liability, and agree to hold them harmless from any claims, losses or damages arising from your use of it or reliance on it. License: Apache 2.0, including its disclaimer of warranty and limitation of liability. Full notice: TERMS.md in this skill's repository.
>
> Reply **"I accept"** to continue.

- Accept only a clear acceptance ("I accept", "I agree", "yes, I accept"). If the reply is ambiguous, ask once more.
- If they decline, don't give plans, recommendations or routes. You can still explain general concepts (what slack water is, how to read a tide table) and point them to the sources in Step 4.
- After a clear acceptance, save it to memory if memory is available, as one dated note naming the version ("Accepted Kayak Trip Planner safety notice v1 on YYYY-MM-DD"), and say so in one line ("Saved your acceptance of the safety notice (v1), so I won't ask again."). If memory isn't available, say it will be asked again in new conversations.
- Ask again whenever you can't confirm an acceptance of the current version: no memory, no matching note, or a note for an older version. Never assume acceptance from anything vaguer than such a note.
- Acceptance is per person. If someone else in the conversation, or a person a plan is shared with, wants their own plan, they accept for themselves.
- When a plan is shared, it already carries its own "Not covered by this plan" section; don't repeat the full notice in every plan.

## Files in this skill

- `scripts/nearest_stations.py` finds the nearest NOAA tide stations, current stations and NDBC buoys to a lat/lon, from the bundled snapshot in `data/`. Runs offline.
- `scripts/sun_times.py` gives sunrise and sunset for a date and place. Runs offline.
- `scripts/sscofs_currents.py` (NOAA SSCOFS: Salish Sea, Columbia River, WA/OR coast) and `scripts/salishsea_currents.py` (SalishSeaCast) give modeled hourly currents at a point, each with a check that the model resolves water near the point. See `references/regional-salish-sea.md`.
- `scripts/build_station_data.py`, `scripts/build_sscofs_mesh.py` and `scripts/build_salishsea_grid.py` rebuild `data/`. Need internet; maintainers run them, not part of planning.
- `references/regional-*.md` hold optional extras for specific regions. Read one only if the launch point is inside its area.
- `references/visual-links.md` has link patterns for graphs, maps and webcams the person can open themselves (tide and current curves, hourly wind graph, live stations, model maps). Read it when the person wants to see the data or a link would clearly help.

Run scripts with `python3 <skill-dir>/scripts/<name>.py --help` for options.

## Step 1: Paddler profile

Use a profile the person has already given (earlier in the conversation or in memory). Otherwise ask once, in one short message, offering these defaults:

- Cruising speed: 2.5 mph (~2.2 kt) for touring kayaks; 2 mph for recreational boats or relaxed groups
- Trip length: 3 hours
- Launch window: when they'd like to start
- Cold-water gear: dry suit, wet suit, or none
- Experience level: beginner, intermediate or advanced (picks the reference conditions in Step 5), or their own limits. **No default.**

Experience level must come from the person. If it isn't known, ask for it, and don't give a plan until they answer; you can pull data meanwhile. For the other items, if the trip is soon and the person seems to want an answer now, proceed with the defaults and say which were assumed. Restate the profile used in every plan. Don't lecture about gear they already have.

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
| Tide shortlist | Past the last marine forecast period | Tides, current-station predictions, daylight | Wind, waves, fog, rain |
| Weather narrowing | Within the marine forecast (usually ~4-5 days) | All above + NWS marine forecast (solid to ~3 days, rough beyond), regional current models within their range | Real-time observations |
| Final check | Today or tomorrow | All above + buoy observations, regional current models (if they pass their close-enough check) | - |

The stage is set per day, not per trip: a week-long window usually mixes stages. The marine point forecast typically ends 4-5 days out (e.g. issued Monday, last period Friday night); days after its last period are tide-shortlist days even if they are within a week. In the tide-shortlist stage, rank days by tide fit and say when to re-check (about 3 days out and the day before).

## Step 4: Pull the data

Fetch with the web-fetch tool. Record each source's URL, issue/update time and the period covered; these go in the plan. If the shell has internet access, `curl` works too; in many environments it doesn't, so don't depend on it.

### Tides (NOAA CO-OPS; horizon: months to years)
```
https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?begin_date=YYYYMMDD&end_date=YYYYMMDD&station=ID&product=predictions&datum=MLLW&time_zone=lst_ldt&interval=hilo&units=english&format=json
```
Many stations are subordinate (secondary) stations that publish only high and low times: `interval=hilo` works, but `interval=h` or `6` returns "No Predictions data was found". When a tide height between the highs and lows is needed (a chart, the water depth at launch time), use cosine interpolation between the bracketing events, NOAA's own method for these stations: h(t) = (h0+h1)/2 + (h0-h1)/2 × cos(π(t-t0)/(t1-t0)). Fetch the events either side of the window, and say the curve is interpolated. Predictions are astronomical; wind and air pressure can shift real water levels by a few tenths of a foot or more. Great Lakes have no meaningful tide; skip this and watch wind-driven water level changes instead.

### Tidal currents (NOAA CO-OPS; horizon: months to years)
```
https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?begin_date=YYYYMMDD&end_date=YYYYMMDD&station=ID&product=currents_predictions&interval=MAX_SLACK&time_zone=lst_ldt&units=english&format=json
```
Add `&bin=N` with the bin from `nearest_stations.py` (the shallowest predicted depth, closest to what a kayak feels; bins count up from the bottom). Returns slack, max flood and max ebb times, speeds in knots (ebb negative) and mean flood/ebb directions.

### Wind, waves, fog, rain (NWS marine point forecast; horizon: usually ~4-5 days)
```
https://forecast.weather.gov/MapClick.php?lat=LAT&lon=LON&unit=0&lg=english&FcstType=text&TextType=1
```
- Use the on-water point. This returns the marine point forecast, with any Small Craft Advisory, Gale Warning or Dense Fog Advisory listed at the top.
- Check for marine advisories and warnings for every candidate day: the hazards listed at the top of the page, and the wording of each forecast period. If shell internet is available, `https://api.weather.gov/alerts/active?point=LAT,LON` also lists active alerts (it may be blocked; don't retry). See "Days this tool doesn't plan" in Step 5.
- ALWAYS check the "Last Update" time. This site sometimes serves a stale cached page that is weeks old, especially for land points or the `FcstType=digital` view. Discard anything not issued in the last ~24 h and list it as unavailable.
- Note the last period listed; that is the forecast horizon. Never extend it.
- Marine forecasts cover broad zones in 5 kt steps. Local gusts, gap winds and afternoon sea breezes can exceed them; say so.

### Real-time observations (NDBC; final-check stage only)
```
https://www.ndbc.noaa.gov/data/realtime2/STATIONID.txt
```
Latest rows first: wind speed and gusts (m/s), wave height (m), water temperature (deg C). `MM` means not measured. Convert units before reporting.
- `nearest_stations.py` labels each NDBC station. Many near shore are **fixed shore or pier stations**, not buoys: they usually report wind and pressure only, no waves or water temperature. Call each one what it is in the plan ("Cherry Point pier weather station, 18.6 mi NW: wind only"), and list waves or water temperature as unavailable if nothing reported them. Never say "buoy data" for a shore station.
- Note distance and exposure: an offshore buoy overstates conditions in a sheltered bay; a sheltered pier station can understate them.
- Readings taken the evening before only describe that evening. For a trip tomorrow, say to check them again the morning of.

### Water temperature
Always find and report it, whatever the gear: it drives the cold-water rule in Step 5 when there is no immersion gear, and with a dry suit or wet suit the person uses it to choose their layers. Report the temperature and its source only. Don't suggest clothing or layers; the person knows their own setup. Sources, in order: a regional model that reports it (in the Salish Sea, `sscofs_currents.py` gives modeled surface water temperature per hour); an NDBC station reporting WTMP; the nearest CO-OPS water level station with `product=water_temperature&date=latest`. Many tide stations don't measure it. If none has it, list it as unavailable; with no immersion gear treat it as below 60 F.

### Daylight
Run `python3 scripts/sun_times.py --lat LAT --lon LON --date YYYY-MM-DD --tz IANA_ZONE`. Flag trips ending within an hour of sunset.

### Regional extras
If a `references/regional-*.md` file covers the launch area, read it and use its sources. These add detail (for example, modeled currents for the Salish Sea) but don't replace the national sources.

Modeled currents beat a distant current station for speed and set near the route, but only where the model actually resolves the water there. Always report the model's distance from the on-water point and its close-enough verdict; if it fails, say the model was checked and didn't apply, and fall back to station timing.

### Access notes
- The web-fetch tool summarizes long pages and truncates large files. Don't fetch NOAA's full station lists; that's what the bundled data is for.
- `api.weather.gov` blocks some automated fetchers. If it fails, use the forecast.weather.gov URL above and don't retry.
- Some map sites (OceanConnect, Windy) render in JavaScript and return nothing to the fetch tool. Offer them for a visual check (see `references/visual-links.md`); never claim to have read them.

## Step 5: Compare each day with reference conditions

### Days this tool doesn't plan
If a **Small Craft Advisory**, or any stronger marine warning (Gale Warning, Storm Warning, Hurricane Force Wind Warning, Hazardous Seas Warning, Special Marine Warning), is in effect at any point during the person's trip window on a day, don't plan that day. Skip the comparison, launch time and route for it. In the table, list the day as "Excluded: <advisory name> in effect <times>", and say once in the plan: "This tool doesn't plan days with a Small Craft Advisory or stronger marine warning; anyone who wants to paddle in those conditions needs to do their own planning." If the advisory's times are unclear, treat the whole day as covered. This is a limit on what the tool plans, not a safety verdict, and applies at every experience level. Re-check advisories at each re-check; one issued or lifted later changes which days are planned.


This is a planning tool, not a safety system. Present the data, compare it with published reference conditions for the person's stated experience level, and point out what may matter. Never call a day, time or route "safe" or "unsafe", and never give a go/no-go verdict; the paddler judges their own skills, group, gear and the water on the day. Use plain comparisons: "within", "near the top of" or "above the reference range for beginners".

Suggesting a best-matching day, a launch time, a direction and a turnaround is part of the plan: it summarizes how the conditions line up with the person's window, speed and level. Rank and suggest on conditions only, and say why in terms of the data ("rising tide all trip, lightest current, only day forecast sunny"). Never use safety words for the ranking or the suggestions: no "safe", "safer", "safest", "less risky", "the safe choice", "you'll be fine", or anything that implies one option protects the paddler more than another. The route reasoning is about effort and timing ("so the return is with the current"), not protection.

### Reference conditions

These come from training standards, not from this skill. They describe the conditions training bodies use for **instructor-led courses** and leader remits at each level, not limits for independent paddling. Say that when you use them, name which set you used, and use the person's own limits instead whenever they give them.

| | Beginner | Intermediate | Advanced |
|---|---|---|---|
| ACA course venue | Level 2, Essentials of Kayak Touring: protected water, landing always available, within 0.5 nm of shore; wind < 10 kt, waves < 1 ft, current < 1 kt | Level 3, Coastal Kayaking: within 1.5 nm of shore, landing always available; wind 10-15 kt, waves 1-2 ft, surf 1-2 ft, current 1-2 kt | Level 4, Open Water Coastal: within 2 nm of shore; wind 15-20 kt, waves 3-5 ft, current 2-4 kt |
| Paddle UK (British Canoeing) environment | Sheltered water: wind up to Beaufort 3 (7-10 kt); open water no more than 200 m offshore; estuaries < 0.5 kt; enclosed bays and harbours, easy landings throughout, no tide races, overfalls or surf | Moderate water (sea): wind up to Beaufort 4 (11-16 kt); up to 2 kt of tide, no races or overfalls; easy landings at most 2 nm apart; crossings up to 2 nm; surf up to 1 m | Advanced water (sea): wind above Beaufort 4; tide races, overfalls or open crossings that can't be avoided; landings may be difficult or impossible; surf up to 1.5 m |

Sources: ACA Level 2 Essentials of Kayak Touring Instructor Criteria, ACA Level 3 Coastal Kayaking Basic Strokes & Rescues Skills Course, ACA Level 4 Open Water Coastal Kayaking Skills Course (all rev. 1/1/2023, americancanoe.org); British Canoeing Awarding Body, Environmental Definitions and Deployment Guidance for Instructors, Coaches and Leaders (V2, April 2025, paddleuk.org.uk). If the person asks where the numbers come from, give these.

The two sets differ (for beginners, ACA allows current up to 1 kt; Paddle UK's sheltered estuaries stop at 0.5 kt). Show the comparison against both when they disagree for a given day, rather than picking one.

### Other things worth pointing out

No standard gives numbers for these; they are common rules of thumb. Mention them as context when they apply, not as limits.
- **Wind against current** builds steep, short waves even at moderate speeds.
- **Offshore wind** (blowing from land to water) makes the return harder and can push a tired paddler away from shore.
- **Afternoon sea breeze** often builds after midday on warm days; heading upwind first keeps the easier leg for last.
- **Fog** cuts visibility for the paddler and for boats looking for them.
- **Thunder or lightning** in the forecast.
- **Cold water**: report the water temperature (see Step 4). Water below about 60 F is commonly cited as a cold-shock concern without immersion gear; mention it only when the person has none.
- **Launch at low tide**: mudflats, long carries, exposed rocks. A rising tide during the trip helps; a falling one can leave boats short of water in shallow bays.

## Step 6: Plan the route

- Do the outbound leg against the weaker push (current or wind) so the return is assisted. Use slack times and the flood/ebb directions to choose.
- Time features to the tide: rocks and tidepools near low water, shallow bays and marshes near high water.
- Distance = speed x duration, minus ~20% for breaks and margin. Give rough clock times for the turnaround and key stops.
- Prefer routes that keep a landing within reach, and note how far from shore the route goes compared with the reference distance for their level (e.g. ACA Level 2: within 0.5 nm; Paddle UK sheltered: within 200 m of shore). Mention crossings of shipping lanes or ferry routes if the route has them.

Local geography is the weakest part of any plan. Name features only when confident; otherwise describe the route by direction and distance ("south along the shore ~2.4 mi, then back") and say to check a chart.

## Step 7: Write the plan

Lead with the suggestion (best-matching day and a backup, and why) and the planning stage. Frame it as the best match for their stated level and preferences, not as a safety call. Then:
- A compact table per candidate day: low/high times and heights, slack and max current times, wind, waves, sky, fog, water temperature, any marine advisory, and how it compares with the reference conditions (or "Excluded" for advisory days).
- Launch time, route and direction, with the reason.
- When to re-check, if the trip is beyond the reliable forecast range.

Then ALWAYS end with this section, filled in, even when everything looks good, followed by the footer line below:

### What this plan is based on
- **Paddler assumptions:** speed, duration, experience level and the reference conditions used (with their source, and that they describe instructor-led course conditions), or the person's own limits; gear; water temperature with its source.
- **Sources checked:** each source with its issue/update time and the period covered (link each); each station's distance from the launch; for current stations, that speeds apply at that station only.
- **Reliability at this lead time:** which parts are predictions (tides, currents) and which are forecasts (weather), and how reliable each is now.
- **Not checked or unavailable:** anything that failed, was stale or was out of range.
- **Excluded:** any day skipped for a Small Craft Advisory or stronger marine warning, with the advisory and its times.
- **Not covered by this plan:** local hazards (rocks, surf, rebound off cliffs, boat and ferry traffic, shipping lanes), closures and permits, launch access, and real-time conditions on the day. This is planning information, not a safety assessment. Look at the water before launching and make your own decision. Conditions change; this plan is not a guarantee of safety.

Footer, last line of every plan, in the upstream sources' own terms: *Planning aid built from NOAA and NWS predictions, forecasts and model guidance, which their providers supply "as is". Not for navigation. Check the official NWS forecast and the water before launching.*

## Refining the plan

Plans already carry a lot of data; keep extra detail for when it's wanted. After the plan, offer in one line the links to graphs, maps and webcams from `references/visual-links.md` instead of listing them, and invite changes, for example: "I want to go south from the launch", "We'll stop for lunch at a beach 2 mi out", "Can we launch at 9?", "Only Thursday works", "Make it 2 hours".
- Treat what the person says about the route, landings and local features as better local knowledge than yours. Use it; don't argue with it unless the data shows a conflict (e.g. their chosen direction means the return is against the stronger current or wind).
- Re-run only what changes: a new direction or destination re-checks Step 6 (outbound/return pushes, distance, turnaround time) with the data already pulled; a new day or time window may need new data, and may change the planning stage.
- If a change moves a factor outside the reference range (e.g. the return leg now meets more current than the beginner reference), say so plainly and mention the alternative; the person decides.
- Re-issue the full plan, including "What this plan is based on", so the latest version stands on its own when shared. Note what changed from the previous version in one line at the top.
