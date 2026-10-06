# Station data (generated)

This folder holds the bundled snapshot of NOAA tide stations, current stations and NDBC weather buoys that `scripts/nearest_stations.py` searches offline. Don't edit these files by hand; rebuild them with:

```
python3 ../scripts/build_station_data.py
```

Files created: `tide_stations.csv`, `current_stations.csv`, `ndbc_stations.csv` and `SNAPSHOT.txt` (build date, counts and source URLs). Rebuild before each release.
