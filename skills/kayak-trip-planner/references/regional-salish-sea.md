# Regional extras: Salish Sea (Puget Sound, San Juan Islands, Bellingham Bay, Strait of Juan de Fuca, Strait of Georgia)

Use when the launch point is roughly between 47.0 and 50.5 N and 122.0 and 125.0 W. These add detail; the national NOAA/NWS sources still come first.

## Modeled surface currents: SalishSeaCast (UBC)
A ~500 m research model of the whole Salish Sea; the model behind the OceanConnect app. Useful in bays and passages with no nearby NOAA current station.

- Dataset page: https://salishsea.eos.ubc.ca/erddap/griddap/ubcSSfDepthAvgdCurrents1h.html
- FIRST fetch `https://salishsea.eos.ubc.ca/erddap/griddap/ubcSSfDepthAvgdCurrents1h.das` and read `time_coverage_end`. That's the real horizon (it has run ~36-48 h ahead). If the trip window is past it, skip this source and list it as out of range.
- Dimensions: `time`, `gridY` (0-897), `gridX` (0-397). Variables (m/s): `VelEast5`, `VelNorth5` (upper 5 levels), `VelEast10`, `VelNorth10`.
- The grid is indexed by cell, not lat/lon. Find the nearest cell with the bathymetry dataset `ubcSSnBathymetryV21-08` on the same server (lat/lon per gridY, gridX). This lookup is not yet tested end to end; if it fails, say so.
- Request a subset as CSV:
  `https://salishsea.eos.ubc.ca/erddap/griddap/ubcSSfDepthAvgdCurrents1h.csv?VelEast5[(START):(END)][(Y)][(X)],VelNorth5[(START):(END)][(Y)][(X)]` with ISO times.
- Speed (kt) = sqrt(E^2 + N^2) x 1.944. Direction the water flows toward = atan2(E, N), in degrees from north.
- Limits: research model; eddies smaller than ~500 m are not resolved.

## Visual check: OceanConnect
https://oceanconnect.ca (Hakai Institute) maps modeled currents, wind, waves and webcams for BC and Washington. It renders in JavaScript, so the fetch tool can't read it. Recommend it to the paddler for a morning-of look, especially the webcams for fog.

## Local notes
- Bellingham Bay / Chuckanut Bay: currents in the bay are weak; wind is the main factor. NOAA's closest current station, PCT2116 off Eliza Island (~3.5 mi W), is rated weak and variable and has no predictions. The nearest stations with predictions are PUG1707 Sinclair Island (~7.7 mi W; flood NW, ebb SE, about 1 kt) and PUG1741 Bellingham Channel North (~8.8 mi WSW; flood N, ebb SW, 2.5-3 kt in the channel). Use them for slack timing only; their directions and speeds describe those channels, not the bay.
- Fall and winter fog often sits on Bellingham Bay and Puget Sound into late morning.
