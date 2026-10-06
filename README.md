# Kayak Trip Planner

A Claude skill that plans sea kayak trips in US waters. Give it a launch point and a few days. It pulls NOAA tide and current predictions, modeled currents, the NWS marine forecast and advisories, live station readings, water temperature and daylight. It compares each day with published reference conditions for your experience level and suggests the best-matching day, launch time and route direction.

Every plan ends with **"What this plan is based on"**: each source, when it was issued, how far it is from your launch, how reliable it is at that lead time, and what wasn't checked. A plan you share stands on its own.

> **Safety notice.** This is a planning tool, not a safety system. It gives general information from public data that can be wrong, late or incomplete. It does not see real conditions, know your abilities or know local hazards, and it never tells you a day is safe. Paddling can cause injury or death. You are responsible for your own decisions and safety. The terms are the [Apache License 2.0](LICENSE) ("as is", no warranty, limited liability: Sections 7 and 8) together with the [Terms of Use and Safety Notice](TERMS.md) (assumption of risk, release and hold harmless). The skill asks you to accept them once, remembers that where Claude has memory, and asks again when the terms version changes.

## Contents
- [What it does, and doesn't](#what-it-does-and-doesnt)
- [Install](#install)
- [Using it](#using-it)
- [Example](#example)
- [What it checks](#what-it-checks)
- [Extra detail for Puget Sound and the Salish Sea](#extra-detail-for-puget-sound-and-the-salish-sea)
- [Reference conditions](#reference-conditions)
- [Notes and limitations](#notes-and-limitations)
- [For maintainers](#for-maintainers)

## What it does, and doesn't

**Does**
- Shows the data for each candidate day side by side and suggests the best match for your stated level and preferences, with a backup.
- Compares wind, waves, current and distance from shore with ACA and Paddle UK reference conditions, or with your own limits if you give them.
- Suggests a launch time and which way to go first so the return leg is easier, with distance and turnaround time from your speed.
- Says when to re-check as forecasts firm up.
- Refines the plan when you tell it what you want ("go south first", "only Thursday works").

**Doesn't**
- Call any day, time or route safe or unsafe, or give go/no-go verdicts. You make the call.
- Plan days with a **Small Craft Advisory** or any stronger marine warning (Gale, Storm, Hurricane Force, Hazardous Seas, Special Marine) during your trip window. Those days are listed as "Excluded". If you want to paddle in those conditions, do your own planning.
- Recommend clothing or gear. It reports water temperature and its source; at 60 °F or colder it also quotes the ACA's own cold-water recommendation, attributed to the ACA.
- Know local hazards, closures, launch access or what the water looks like today.

## Install

### claude.ai (web, desktop and mobile)
The repository is a plugin marketplace, so claude.ai can install it straight from GitHub and keep it up to date.

1. Open **Customize > Plugins**, then **Add > Add marketplace**.
2. Enter `PNWSoft/kayak-trip-skill`.
3. Install **kayak-trip-planner** from that marketplace.
4. Turn on **Sync automatically** so each push to `main` updates your copy. (**Check for updates** does it by hand.)
5. Make sure **Settings > Capabilities > Code execution and file creation** is on. The skill runs small Python scripts.

If you previously uploaded the skill as a zip, remove that copy so the two don't compete for the same questions.

<details>
<summary>Alternative: upload a zip</summary>

```
cd skills && zip -r ../kayak-trip-planner.zip kayak-trip-planner
```
The zip must contain `kayak-trip-planner/SKILL.md` at its top level (a `SKILL.md` at the root of the zip isn't recognized). Upload it as a custom skill and turn it on under **Customize > Skills**. A zip doesn't update itself; re-upload after changes.
</details>

### Claude Code
```
/plugin marketplace add PNWSoft/kayak-trip-skill
/plugin install kayak-trip-planner@kayak-trip-planner
```
Developing locally? Add your clone as the marketplace instead, so edits take effect without reinstalling:
```
claude plugin marketplace add /path/to/kayak-trip-skill
claude plugin install kayak-trip-planner@kayak-trip-planner
```
Then run `/reload-plugins` in the session (or `/reload-plugins --force`).

### Team and Enterprise organizations
Owners can push it to everyone under **Organization settings > Plugins & skills > Add > Sync from GitHub**. That option only accepts **private or internal** repositories, so fork this repo into a private one first. With **Sync automatically** on, each push to the default branch updates members. Members find it under **Customize > Plugins**.

References: [Plugins overview](https://claude.com/docs/plugins/overview.md), [Skills how-to](https://claude.com/docs/skills/how-to.md), [Org sync from GitHub](https://claude.com/docs/plugins/org-sync.md).

## Using it

Ask in plain language. Name a launch (or give coordinates), a day range and roughly when you'd start.

> Is there a good day this week to kayak from Wildcat Cove in Chuckanut Bay, WA? We'd leave 10am-noon for about 3 hours.

> This week I want to kayak starting sometime from 10am-12pm, from either Wildcat Cove or Marine Park in Whatcom County, WA. What's the best day to go?

> We're thinking Deception Pass next Saturday morning. When is slack, and is the weather looking OK?

**What it asks first**
1. **The terms.** Reply **"I accept"**; it won't plan until you do. With Claude's memory on it saves your acceptance and doesn't ask again until the terms version changes; without memory it asks in each new conversation.
2. **Your profile**, once: cruising speed (default 2.5 mph touring, 2 mph relaxed), trip length (default 3 hours), launch window, cold-water gear, and **experience level** (beginner, intermediate, advanced, or your own limits). Experience level has no default; it always asks.

**Refining the plan**
> I want to go south from Wildcat Cove.
> We'll stop for lunch at a beach about 1.5 miles out.
> Only Thursday works. Can we launch at 9?
> Make it 2 hours.

It re-plans and re-issues the whole plan, noting what changed at the top. What you say about the route and local features counts as better local knowledge than its own.

**Seeing the data yourself**
> Show me the tide and current graphs for Thursday.
> Where can I check for fog Thursday morning?
> Make a chart of Thursday's tide and current.

It keeps links to NOAA tide and current graphs, the NWS hourly wind graph, live station pages, model maps and webcams ([`references/visual-links.md`](skills/kayak-trip-planner/references/visual-links.md)) and offers them instead of putting them all in every plan.

## Example

From a test run on Monday Oct 5, 2026: beginner, 2 mph, 3 hours, launch 10am-noon, dry suit, Wildcat Cove (WC) or Marine Park (MP).

**Best match: Thursday Oct 8, Wildcat Cove, launch around 10:30am. Backup: Wednesday Oct 7, either launch.**

| Day | Tide (Bellingham) | Wind / waves | Sky | Current off launch | Water | Advisory | vs. beginner references |
|---|---|---|---|---|---|---|---|
| Tue 6 | L 0.3 ft 08:07 → H 8.4 ft 15:39 | Variable ≤5 kt / ≤1 ft | Mostly cloudy | ≤0.3 kt | 56-57 °F | None | Within |
| Wed 7 | L 0.8 ft 09:05 → H 8.4 ft 16:09 | Variable ≤5 kt / ≤1 ft | AM cloud, clearing | ≤0.3 kt | 56-57 °F | None | Within |
| **Thu 8** | L 1.5 ft 09:55 → H 8.4 ft 16:34 | Variable ≤5 kt / ≤1 ft | Mostly sunny | ≤0.2 kt NNW | 55-56 °F | None | Within |
| Fri 9 | L 2.3 ft 10:39 → H 8.3 ft 16:55 | WC S 5-7 kt; MP SSE 5-11 kt | Chance of rain | beyond model range | – | None | WC within; MP wind above |
| Sat 10 | L 3.2 ft 11:21 → H 8.2 ft 17:13 | not yet forecast | – | – | – | Re-check | Tides only |

The plan then gives the route (south first along the shore against the weak set, turn around about 12:00, back about 1:30, ~2.4 mi each way), when to re-check, and the full "What this plan is based on" section.

## What it checks

| Factor | Source | How far ahead |
|---|---|---|
| Tides | NOAA CO-OPS tide predictions | Months to years |
| Tidal current timing (slack, flood, ebb) | NOAA CO-OPS current predictions | Months to years |
| Wind, waves, sky, rain, fog | NWS marine point forecast | Usually 4-5 days |
| Marine advisories and warnings | NWS marine forecast and active alerts | Current |
| Modeled current and water temperature at a point | NOAA SSCOFS; SalishSeaCast (UBC) as a cross-check | ~2-3 days (Salish Sea, Columbia River, WA/OR coast) |
| Live wind (and waves or water temperature where measured) | NDBC buoys and shore stations | Real time |
| Water temperature | Regional model, NDBC, or CO-OPS stations | Varies |
| Sunrise and sunset | Computed offline | Any date |

**Coverage:** US coastal waters, estuaries and the Great Lakes. Inland lakes and rivers get the land forecast only. Outside the US, the sources don't apply and it says so.

### Extra detail for Puget Sound and the Salish Sea
The skill works anywhere in US coastal waters, but it has extra data for one region, where it was built and tested:

| | Everywhere in the US | Also in the Salish Sea region |
|---|---|---|
| Tides, current-station timing, NWS forecast and advisories, NDBC stations, daylight | ✓ | ✓ |
| **Modeled current at your launch** (speed and direction hour by hour, not just a distant channel station) | – | ✓ NOAA SSCOFS, with UBC SalishSeaCast as a cross-check |
| **Modeled water temperature** near your launch | – (only where an NDBC or CO-OPS station measures it) | ✓ NOAA SSCOFS |
| Local notes (station quirks, fog patterns, model accuracy) | – | ✓ [`regional-salish-sea.md`](skills/kayak-trip-planner/references/regional-salish-sea.md) |

**The Salish Sea region** covers Puget Sound, Hood Canal, the San Juan Islands, Bellingham Bay, the Strait of Juan de Fuca and the Strait of Georgia (SalishSeaCast includes the BC side). NOAA SSCOFS also covers the **Columbia River and the Washington and Oregon outer coast**.

**Elsewhere** the plan relies on the nearest NOAA current station for timing only, and says so, because channel speeds can be far from what you'll meet near shore. NOAA runs similar models for other regions (Chesapeake Bay, San Francisco Bay, Delaware Bay, Tampa Bay, the Great Lakes and more), but the skill doesn't read them yet. Regional notes and model support for other areas are welcome; see [Contributing](#contributing).

**Planning stage, set per day:** days past the last marine forecast period get tides and daylight only ("tide shortlist"); days within the forecast add weather and models ("weather narrowing"); today and tomorrow add live readings ("final check"). It never treats data past its horizon as a forecast.

## Reference conditions

The comparisons use published training standards. They describe conditions that training bodies use for **instructor-led courses** at each level, not limits for independent paddling, and every plan says so. Give your own limits and it uses those instead.

| | Beginner | Intermediate | Advanced |
|---|---|---|---|
| ACA course venue | Level 2: protected water within 0.5 nm of shore; wind < 10 kt, waves < 1 ft, current < 1 kt | Level 3: within 1.5 nm; wind 10-15 kt, waves 1-2 ft, current 1-2 kt | Level 4: within 2 nm; wind 15-20 kt, waves 3-5 ft, current 2-4 kt |
| Paddle UK environment | Sheltered: wind up to Beaufort 3 (7-10 kt); within 200 m of shore; estuaries < 0.5 kt; easy landings | Moderate (sea): up to Beaufort 4 (11-16 kt); tide up to 2 kt; landings ≤ 2 nm apart | Advanced: above Beaufort 4; races, overfalls, open crossings |

Sources: ACA [Level 2](https://americancanoe.org/download/5028/sei-courses/23136/level_2_essentials_of_kayak_touring_instructor_criteria.pdf), [Level 3](https://americancanoe.org/download/5028/sei-courses/23231/level_3_coastal_kayaking_basic_strokes__rescues_skills_course.pdf) and [Level 4](https://americancanoe.org/download/5028/sei-courses/23391/level_4_open_water_coastal_kayaking_skills_course.pdf) course documents (rev. 1/1/2023); British Canoeing Awarding Body, [Environmental Definitions](https://paddleuk.org.uk/shared-files/17357/Environmental-Definitions-4Jan23.pdf) (V2, April 2025).

Fog, thunder, cold water, wind against current, offshore wind and low-tide launches have no standard numbers; the plan mentions them as context when they apply.

## Notes and limitations

- **Distant current stations give timing, not speed.** NOAA current stations are often in channels miles away, running several times faster than a nearby bay. Plans use them for slack and flood/ebb timing only and say so.
- **Weak-and-variable stations are skipped.** NOAA type "W" current stations have no predictions. If one is closer than the usable stations, the plan notes that NOAA rates currents near the launch as weak.
- **Models need a close-enough check.** The model scripts reject points where the nearest model water is more than 1 km away (small coves, narrow passes, lakes) and flag cells beyond 400 m or next to shore. SSCOFS is fine enough for most passes; SalishSeaCast (~500 m cells) isn't. At Deception Pass, SSCOFS got the timing within ~20-30 min but peak speeds 30-50% low, so NOAA predictions come first where a station sits on the route.
- **Some tide stations publish highs and lows only.** Heights in between are cosine-interpolated, NOAA's own method, and labelled as such.
- **Many "buoys" are shore stations.** Near shore, NDBC stations are often piers or docks reporting wind only. Plans name what each station is and what it reported.
- **The marine forecast is a broad zone in 5 kt steps.** Local gusts, gap winds and afternoon sea breezes can exceed it.
- **Geography is the weakest part.** The skill names local features only when confident and otherwise describes the route by direction and distance. Your local knowledge wins.
- **Scripts and internet on claude.ai.** If the scripts can't reach the internet there, the skill uses its web-fetch tool instead; the model scripts' `--url-only` mode does the offline checks and prints the small data URLs to fetch. This path is less tested than Claude Code.
- **Sites that draw in the browser** (OceanConnect, Windy) can't be read by the skill. It offers them for your own look and never claims to have used them.

## For maintainers

### Scripts
All scripts take `--help`. Run from `skills/kayak-trip-planner/`.
```
# nearest NOAA tide and current stations and NDBC stations (offline)
python3 scripts/nearest_stations.py --lat 48.655 --lon -122.49 --n 3

# sunrise and sunset (offline)
python3 scripts/sun_times.py --lat 48.655 --lon -122.49 --date 2026-10-08 --tz America/Los_Angeles

# modeled current and water temperature at an on-water point, NOAA SSCOFS
python3 scripts/sscofs_currents.py --lat 48.656 --lon -122.505 --date 2026-10-08 --start 10:00 --hours 4

# modeled current, SalishSeaCast (UBC)
python3 scripts/salishsea_currents.py --lat 48.656 --lon -122.505 --date 2026-10-08 --start 10:00 --hours 4
```
Model scripts exit 0 with data, 1 if data was unavailable, 2 if the model doesn't resolve the point, and 3 if the window is past the forecast. Add `--json` for machine-readable output or `--url-only` to skip fetching.

### Refreshing bundled data
Rebuild before each release (needs internet):
```
python3 skills/kayak-trip-planner/scripts/build_station_data.py    # NOAA stations and NDBC (~0.5 MB)
python3 skills/kayak-trip-planner/scripts/build_sscofs_mesh.py     # SSCOFS mesh index (~4 MB)
python3 skills/kayak-trip-planner/scripts/build_salishsea_grid.py  # SalishSeaCast water cells (~0.8 MB)
```
No internet? `build_station_data.py --from-dir` reads the three source files downloaded in a browser; see its `--help`. Rebuild the SSCOFS index if NOAA changes the model mesh.

### Repository layout
```
.claude-plugin/
  plugin.json               plugin manifest
  marketplace.json          lets this repo act as its own marketplace
skills/kayak-trip-planner/
  SKILL.md                  the instructions Claude follows
  scripts/                  station lookup, daylight, model currents, data builders
  data/                     bundled station snapshot and model indexes (generated)
  references/
    regional-salish-sea.md  Salish Sea models, local notes
    visual-links.md         links to graphs, maps and webcams
TERMS.md                    terms of use and safety notice (versioned); applies with the license
PRIVACY.md                  privacy policy (the authors collect no data)
SUPPORT.md                  no support provided; feedback via GitHub issues
LICENSE                     Apache License 2.0 (code)
```

### Contributing
Regional notes are the most useful contribution: a `references/regional-<area>.md` file describing extra sources (regional models, local wind patterns, known hazards, nearby stations, common routes and landings) for a stretch of coast you know well. Follow the Salish Sea file as a template. Keep every source public and free, and say what it does and doesn't cover.

## Data sources and attribution
Tide and current predictions and the SSCOFS model from NOAA CO-OPS (tidesandcurrents.noaa.gov). Marine forecasts and alerts from the National Weather Service (weather.gov). Station observations from NOAA's National Data Buoy Center (ndbc.noaa.gov). SalishSeaCast modeled currents from the University of British Columbia. Reference conditions from the American Canoe Association and British Canoeing / Paddle UK. None of these organizations is affiliated with or endorses this tool.

## License
Terms: the [Apache License 2.0](LICENSE) together with the [Terms of Use and Safety Notice](TERMS.md); both apply to the tool and its output.
