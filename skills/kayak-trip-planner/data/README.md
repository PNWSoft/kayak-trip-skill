# Bundled data (generated)

These files let the scripts work offline. Don't edit them by hand; rebuild them with the scripts below (they need internet). Rebuild before each release.

| File | What it is | Rebuilt by | Build record |
|---|---|---|---|
| `tide_stations.csv`, `current_stations.csv`, `ndbc_stations.csv` | NOAA CO-OPS tide and current prediction stations and NDBC weather stations, for `nearest_stations.py` | `scripts/build_station_data.py` | `SNAPSHOT.txt` |
| `sscofs_mesh.csv.gz` | NOAA SSCOFS mesh index (element centres, depth, shoreline sides, a corner node), for `sscofs_currents.py` | `scripts/build_sscofs_mesh.py` | `sscofs_mesh.meta.json` (counts are checked against the live model) |
| `salishsea_grid.csv.gz` | SalishSeaCast (UBC) water cells, for `salishsea_currents.py` | `scripts/build_salishsea_grid.py` | `salishsea_grid.meta.json` |

```
python3 ../scripts/build_station_data.py
python3 ../scripts/build_sscofs_mesh.py
python3 ../scripts/build_salishsea_grid.py
```
