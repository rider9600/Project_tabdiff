# Data card

**Status (23 November 2026): T-Drive not yet downloaded.** Microsoft's server refuses automated
downloads (challenge 6), so the user downloads it in a browser into `data_raw/tdrive/`.

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

### T-Drive

To fill in once downloaded: files, rows, map-matching success rate, traversals, transactions, the
chosen area, the number of segment columns, and the MD5s of the clean files.
