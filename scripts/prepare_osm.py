"""Build the Beijing drivable road graph from a local OpenStreetMap extract and save it as GraphML.

Follows Rathan, Reddy & Mondal (2022): nodes are intersections, directed edges are road segments.
The area is a bounding box around Beijing's 5th Ring Road, the region used in that paper.

Input: the BBBike Beijing extract, downloaded once into data_raw/osm/:
    https://download.bbbike.org/osm/bbbike/Beijing/Beijing.osm.gz
(The public Overpass API timed out on this area and asks automated users not to load it, so the
graph is built from the extract instead.)

    .venv/Scripts/python scripts/prepare_osm.py

Steps:
1. Load every highway way from the extract, unsimplified, keeping one-way directions.
2. Keep drivable public roads with the same rules as osmnx's "drive" network type.
3. Cut to the bounding box and keep the largest weakly connected component.
4. Simplify (merge chains of degree-2 nodes into single road segments).

Writes data_raw/osm/beijing_5th_ring_drive.graphml and data_raw/osm/osm_report.json.
"""

import hashlib
import json
import re
import time
from pathlib import Path

import networkx as nx
import osmnx as ox

# Approximate bounding box of Beijing's 5th Ring Road (degrees). West, south, east, north.
BBOX = (116.20, 39.75, 116.55, 40.03)
OUT_DIR = Path(__file__).resolve().parents[1] / "data_raw" / "osm"
EXTRACT = OUT_DIR / "Beijing.osm.gz"
GRAPH_FILE = OUT_DIR / "beijing_5th_ring_drive.graphml"

# osmnx 2.1 "drive" filter (osmnx._overpass._get_network_filter("drive")), applied locally.
# Each rule: tag, unanchored regex that must NOT match (Overpass "!~" semantics).
DRIVE_EXCLUDE = {
    "area": r"yes",
    "access": r"private",
    "highway": r"abandoned|bridleway|bus_guideway|construction|corridor|cycleway|elevator|escalator"
               r"|footway|no|path|pedestrian|planned|platform|proposed|raceway|razed|rest_area"
               r"|service|services|steps|track",
    "motor_vehicle": r"no",
    "motorcar": r"no",
    "service": r"alley|driveway|emergency_access|parking|parking_aisle|private",
}


def md5(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def is_drivable(data: dict) -> bool:
    if "highway" not in data:
        return False
    for tag, pattern in DRIVE_EXCLUDE.items():
        value = data.get(tag)
        if value is not None and re.search(pattern, str(value)):
            return False
    return True


def main() -> None:
    if not EXTRACT.exists():
        raise SystemExit(f"missing {EXTRACT}: download the BBBike Beijing extract first (see docstring)")
    start = time.time()
    for tag in ("motor_vehicle", "motorcar"):
        if tag not in ox.settings.useful_tags_way:
            ox.settings.useful_tags_way = list(ox.settings.useful_tags_way) + [tag]

    raw = ox.graph_from_xml(EXTRACT, simplify=False, retain_all=True)
    counts = {"raw_nodes": raw.number_of_nodes(), "raw_edges": raw.number_of_edges()}

    drop = [(u, v, k) for u, v, k, d in raw.edges(keys=True, data=True) if not is_drivable(d)]
    raw.remove_edges_from(drop)
    raw.remove_nodes_from([n for n in list(raw.nodes) if raw.degree(n) == 0])
    counts["drive_edges_before_bbox"] = raw.number_of_edges()

    graph = ox.truncate.truncate_graph_bbox(raw, BBOX)
    largest = max(nx.weakly_connected_components(graph), key=len)
    graph = graph.subgraph(largest).copy()
    graph = ox.simplify_graph(graph)
    ox.save_graphml(graph, GRAPH_FILE)

    report = {
        "source": "OpenStreetMap, BBBike Beijing extract (download.bbbike.org/osm/bbbike/Beijing/)",
        "extract_file": EXTRACT.name,
        "extract_md5": md5(EXTRACT),
        "osmnx_version": ox.__version__,
        "bbox_west_south_east_north": BBOX,
        "filter": "osmnx 2.1 'drive' rules applied locally",
        **counts,
        "nodes": graph.number_of_nodes(),
        "directed_edges": graph.number_of_edges(),
        "strongly_connected_nodes": len(max(nx.strongly_connected_components(graph), key=len)),
        "graphml": GRAPH_FILE.name,
        "graphml_md5": md5(GRAPH_FILE),
        "built": time.strftime("%Y-%m-%d %H:%M:%S"),
        "seconds": round(time.time() - start, 1),
    }
    (OUT_DIR / "osm_report.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
