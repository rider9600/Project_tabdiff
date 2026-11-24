# Data card

**Status (24 November 2026): T-Drive downloaded, profiled and cleaned.** Microsoft's server refuses
automated downloads (challenge 6), so the user downloaded it in a browser. The copy is a mirror
("T-drive Taxi Trajectories.zip", 153,217,794 bytes, MD5 `96f5fd804fbe86b1107c88bc3865b0d0`). Its
contents match the official release: 10,357 taxi files plus Microsoft's user_guide.pdf (version 1.0,
12 August 2011).

**Licence (user guide section 5, Microsoft Research License Agreement):** non-commercial use only
(teaching and academic research are allowed). **"You may not distribute this Software or any derivative
works in any form."** So raw data, cleaned data, transactions and synthetic data files never go on
GitHub or anywhere public. They stay on the laptop and the user's own Ada account. Tables, figures and
metrics in the report are fine; cite the two papers below.

**Official files** (page: https://www.microsoft.com/en-us/research/publication/t-drive-trajectory-data-sample/):
- `06.zip`, `07.zip`, `08.zip`, `09.zip`, `010.zip`, `011.zip`, `012.zip`, `013.zip`, `014.zip` under
  `https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/` (the page labels them "PDF",
  but they are zips). Also mirrored as one OneDrive link on the same page.
- User guide: `https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/User_guide_T-drive.pdf`
- Format (GeoMesa documentation): one text file per taxi, rows `taxi id, timestamp, longitude, latitude`.

| Dataset | Source link | Citation | Train / validation / test | Licence note |
|---|---|---|---|---|
| T-Drive (Beijing taxi GPS, 10,357 taxis, 2 to 8 February 2008, ~15M points, ~177 s sampling) | See "Official files" above | Requested by the dataset page: Yuan, Zheng, Zhang, Xie, Xie, Sun & Huang, "T-drive: driving directions based on taxi trajectories", ACM SIGSPATIAL GIS 2010, pp. 99-108; Yuan, Zheng, Xie & Sun, "Driving with knowledge from the physical world", KDD 2011 (check exact BibTeX before citing) | to define: split by transaction, 70 / 10 / 20, after map-matching | No licence text on the page; read the terms in the user guide PDF |
| OpenStreetMap road network of Beijing (via OSMnx) | BBBike Beijing extract, https://download.bbbike.org/osm/bbbike/Beijing/Beijing.osm.gz (downloaded 23 November 2026; extract dated 22 November 2026) | OpenStreetMap contributors; Boeing, OSMnx (check the citation) | n/a | ODbL |
| Fallback only: Geolife | Microsoft Research | Zheng et al., Geolife (check before citing) | n/a | Non-commercial research use |

## Cleaning

### Road graph (23 November 2026, scripts/prepare_osm.py)

| Step | Count |
|---|---|
| All highway ways in the extract, unsimplified | 2,093,327 nodes, 4,275,184 directed edges |
| After the osmnx "drive" rules (whole extract) | 589,613 directed edges |
| Cut to the 5th Ring box (116.20 to 116.55 E, 39.75 to 40.03 N), largest weakly connected component, simplified | **34,135 intersections, 76,592 directed road segments** |
| Largest strongly connected component | 33,679 intersections (98.7%) |

Checks on the output: node coordinates span exactly the box; total road length 12,638 km; segment
length median 110 m, mean 165 m, max 6,218 m; 26,096 one-way segments; most common types are
residential (32,009), tertiary (18,642), unclassified, secondary, primary and trunk.

MD5: extract `e3a0799ee79ed204159fe2ecbda11c36`; GraphML `846eaf436af874e173366db2bbdbfc05`.

**Consequence for the encoding:** 76,592 directed segments would be 76,592 TabDiff columns, far too
many. This confirms that columns must be restricted (decision 6): a smaller area and/or only the
segments that taxis actually use often.

### T-Drive profile (24 November 2026, scripts/profile_tdrive.py, all rows)

| Check | Result |
|---|---|
| Files / non-empty / taxis with data | 10,357 / 10,336 / 10,336 |
| Rows | 17,662,984 |
| Repeated (taxi, time) rows | 1,341,490 |
| Zero coordinates / outside Beijing | 38,626 / 171,379 |
| Inside the 5th Ring box | 12,623,453 (71%) |
| Time range | 2008-02-02 13:30:44 to 2008-02-08 17:39:19 |
| Interval between points (s) | median 212, mean 321; quantiles 0.25: 19, 0.75: 300, 0.99: 1,508 |
| Gaps over 15 min / 30 min / 60 min | 309,415 / 132,578 / 82,113 |
| Consecutive pairs moving under 10 m | 5,942,783 of 16,311,158 (36%, parked or waiting) |
| Pairs implying over 150 km/h | 90,622 |
| Points per taxi | median 1,262; 0.1 quantile 346; 0.99 quantile 7,960 |

### T-Drive cleaning (24 November 2026, scripts/clean_tdrive.py)

| Step | Points left |
|---|---|
| Raw | 17,662,984 |
| Drop repeated (taxi, time) | 16,321,494 |
| Drop zero coordinates | 16,284,564 |
| Drop GPS spikes (speed in and out above 150 km/h), pass 1 / pass 2 | 16,237,199 / 16,237,199 |
| Keep the 5th Ring box | **11,768,462 points, 10,207 taxis** |

Output `data_clean/tdrive_points.parquet`, MD5 `80b6801a6f601e592de99201d846bc40`.

Still to fill in: map-matching success rate, traversals, transactions, the chosen area, the number of
segment columns.
