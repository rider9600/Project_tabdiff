# Data card

**Status (23 November 2026): nothing downloaded yet.** Ask the user before downloading (slow connection).

| Dataset | Source link | Citation | Train / validation / test | Licence note |
|---|---|---|---|---|
| T-Drive (Beijing taxi GPS, 10,357 taxis, 2 to 8 February 2008, ~15M points, ~177 s sampling) | Microsoft Research T-Drive trajectory data sample (download page to confirm before downloading) | Yuan et al., "T-Drive: driving directions based on taxi trajectories", ACM SIGSPATIAL GIS 2010; Yuan et al., "Driving with knowledge from the physical world", KDD 2011 (check both on the web before citing, rules/06) | to define: split by transaction, 70 / 10 / 20, after map-matching | Non-commercial research use; read the licence page once |
| OpenStreetMap road network of Beijing (via OSMnx) | https://www.openstreetmap.org | OpenStreetMap contributors; Boeing, OSMnx (check the citation) | n/a | ODbL |
| Fallback only: Geolife | Microsoft Research | Zheng et al., Geolife (check before citing) | n/a | Non-commercial research use |

## Cleaning

To fill in as it happens: steps, rows removed per step, map-matching success rate, number of
traversals and transactions, the chosen area, number of segment columns, and the MD5s of the clean files.
