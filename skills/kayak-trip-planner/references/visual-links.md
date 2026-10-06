# Links for the paddler's own visual check

Graphs, maps and webcams the person can open themselves. Most render in the browser, so the fetch tool can't read them: never imply a plan used them.

Don't list these in every plan. Plans already carry a lot of data. Offer them in one line ("I can give you links to tide and current graphs, the hourly wind graph and webcams"), and give the ones that fit when the person asks or when a link clearly helps (e.g. webcams for a morning fog check, the hourly wind graph when wind timing is close). Build links only from the station IDs, bins and points used in the plan; these pages show a normal-looking page even for a wrong ID.

Tested 2026-10-05 with the Wildcat Cove plan.

## Anywhere in the US

| What it shows | URL pattern | Notes |
|---|---|---|
| Tide curve and high/low table for a station | `https://tidesandcurrents.noaa.gov/noaatidepredictions.html?id=TIDE_ID` | NOAA CO-OPS. Same predictions the plan uses, as a graph. |
| Current curve (flood, ebb, slack) for a station | `https://tidesandcurrents.noaa.gov/noaacurrents/predictions?id=CURRENT_ID_BIN` | e.g. `PUG1741_27`. Same bin as the plan. Speeds apply at that station only. |
| Hourly wind, gusts, sky and rain chance graph | `https://forecast.weather.gov/MapClick.php?lat=LAT&lon=LON&unit=0&lg=english&FcstType=graphical` | NWS. Use the on-water point. Shows its own "Last Update"; same staleness rule as the text forecast. |
| Point forecast page with any hazards at the top | `https://forecast.weather.gov/MapClick.php?lat=LAT&lon=LON` | NWS. Good for a quick look at advisories. |
| Live wind (and waves or water temp, if measured) | `https://www.ndbc.noaa.gov/station_page.php?station=STATION_ID` | NDBC. Use the station from the plan; say if it's a shore station. |
| Wind and wave map | `https://www.windy.com/?LAT,LON,12` | Commercial site, free to view. Model maps, not observations. Optional; offer only if the person wants a map. |

## Salish Sea and Columbia River

| What it shows | URL | Notes |
|---|---|---|
| Modeled current, water level and temperature maps | `https://tidesandcurrents.noaa.gov/ofs/sscofs/sscofs.html` | NOAA SSCOFS, the model the plan uses. Regional maps; pick the subdomain. |
| Modeled currents, wind, waves and webcams | `https://oceanconnect.ca/` | Hakai Institute / CIOOS Pacific, uses UBC's SalishSeaCast. Webcams are the best quick fog check. |
| SalishSeaCast results | `https://salishsea.eos.ubc.ca/nemo/results/` | UBC research model; figures by day. |
