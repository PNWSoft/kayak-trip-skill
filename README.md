# Kayak Trip Planner

A Claude skill that plans sea kayak trips in US waters. Give it a launch point and a few days, and it pulls NOAA tide and current predictions, the NWS marine forecast, buoy observations and daylight, checks each against your skill level, and recommends the best day, launch time and route direction. Every plan ends with a section listing exactly which sources it used, how reliable they are at that lead time, and what it didn't check, so a plan you share can stand on its own.

> **Safety notice.** This tool gives general planning information from public data that can be wrong or out of date. It does not see real conditions or know local hazards, and it is not a guarantee of safety. Paddling can cause injury or death. You are responsible for your own decisions and safety. Use of the tool requires accepting the [Terms of Use](TERMS.md), which include an assumption of risk, a release and a hold-harmless agreement. The skill asks you to accept them before giving its first plan in each conversation.

## What it checks

| Factor | Source | How far ahead |
|---|---|---|
| Tides | NOAA CO-OPS tide predictions | Months to years |
| Tidal currents (slack, flood, ebb) | NOAA CO-OPS current predictions | Months to years |
| Wind, waves, fog, rain, advisories | NWS marine point forecast | About 5-7 days |
| Live wind, waves, water temperature | NDBC buoys | Real time |
| Sunrise and sunset | Computed offline | Any date |
| Modeled currents at a point (NOAA SSCOFS, SalishSeaCast) | Salish Sea, Columbia River, WA/OR coast | ~2-3 days |
| Other regional extras | See `references/` | Varies |

Coverage: US coastal waters, estuaries and the Great Lakes. Inland lakes and rivers get the land forecast only.

## How it works

1. **Accepts terms** once per conversation (see TERMS.md).
2. **Asks for your profile** once: speed, trip length, skill level, cold-water gear. Thresholds for wind, waves and current adjust to your skill level.
3. **Finds the nearest stations** from a bundled snapshot of every NOAA tide station, current station and NDBC weather buoy. This runs offline, so it works even where Claude can't download large files.
4. **Picks the planning stage** from how far out the trip is (tide shortlist, weather narrowing or final check) and never treats data past its horizon as a forecast.
5. **Writes the plan**: best day and backup, a per-day table, launch time and route direction, when to re-check, and "What this plan is based on".

## Install

### Claude Code
```
/plugin marketplace add PNWSoft/kayak-trip-skill
/plugin install kayak-trip-planner@kayak-trip-planner
```
Once listed in Anthropic's community marketplace:
```
/plugin marketplace add anthropics/claude-plugins-community
/plugin install kayak-trip-planner@claude-community
```

### Claude app (claude.ai, desktop, mobile)
Download `kayak-trip-planner.zip` from the latest release (it contains the `skills/kayak-trip-planner` folder) and upload it as a custom skill. See [Using skills in Claude](https://support.claude.com/en/articles/12512180-using-skills-in-claude).

### Try it
> "Is there a good day this week to kayak from Wildcat Cove in Chuckanut Bay, WA? We'd leave 10am-noon for about 3 hours."

## Repository layout

```
.claude-plugin/
  plugin.json             plugin manifest
  marketplace.json        lets this repo act as its own marketplace
skills/kayak-trip-planner/
  SKILL.md                the instructions Claude follows
  scripts/
    nearest_stations.py   nearest tide/current stations and buoys (offline)
    sun_times.py          sunrise/sunset (offline)
    sscofs_currents.py    modeled currents at a point, NOAA SSCOFS (Salish Sea, Columbia R., WA/OR coast)
    salishsea_currents.py modeled currents at a point, SalishSeaCast
    build_station_data.py rebuilds the station snapshot (maintainers)
    build_salishsea_grid.py rebuilds the SalishSeaCast cell table (maintainers)
    build_sscofs_mesh.py  rebuilds the SSCOFS mesh index (maintainers)
  data/                   station snapshot (generated; see SNAPSHOT.txt)
  references/
    regional-salish-sea.md
TERMS.md                  terms of use, assumption of risk, hold harmless
LICENSE                   Apache License 2.0 (code)
```

## Refreshing the station data

Stations change rarely, but rebuild the snapshot before each release:
```
python3 skills/kayak-trip-planner/scripts/build_station_data.py
```
No internet in your environment? Download the three source files listed in the script's `--help` in a browser and use `--from-dir`.

## Contributing

Regional notes are the most useful contribution: a `references/regional-<area>.md` file describing extra sources (regional models, local wind patterns, known hazards and nearby stations) for a stretch of coast you know well. Follow the Salish Sea file as a template. Please keep every source public and free, and state what it does and doesn't cover.

## Data sources and attribution

Tide and current predictions from NOAA CO-OPS (tidesandcurrents.noaa.gov). Marine forecasts from the National Weather Service (weather.gov). Buoy observations from NOAA's National Data Buoy Center (ndbc.noaa.gov). Salish Sea modeled currents from the SalishSeaCast project, University of British Columbia. These agencies and projects are not affiliated with and do not endorse this tool.

## License

Code: [Apache License 2.0](LICENSE). Use of the tool and its output: [Terms of Use](TERMS.md).
