"""Download the Beijing drivable road network from OpenStreetMap and save it as GraphML.

Follows Rathan, Reddy & Mondal (2022): nodes are intersections, directed edges are road segments.
The area is a bounding box around Beijing's 5th Ring Road, the region used in that paper.

    .venv/Scripts/python scripts/prepare_osm.py

Writes data_raw/osm/beijing_5th_ring_drive.graphml and data_raw/osm/osm_report.json
(counts, bounding box, osmnx version, MD5 of the GraphML file).
"""

import hashlib
import json
import time
from pathlib import Path

import osmnx as ox

# Approximate bounding box of Beijing's 5th Ring Road (degrees). West, south, east, north.
BBOX = (116.20, 39.75, 116.55, 40.03)
OUT_DIR = Path(__file__).resolve().parents[1] / "data_raw" / "osm"
GRAPH_FILE = OUT_DIR / "beijing_5th_ring_drive.graphml"


def md5(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ox.settings.use_cache = True
    ox.settings.cache_folder = str(OUT_DIR / "cache")
    start = time.time()
    graph = ox.graph_from_bbox(BBOX, network_type="drive", simplify=True)
    ox.save_graphml(graph, GRAPH_FILE)
    report = {
        "source": "OpenStreetMap via osmnx (Overpass API)",
        "osmnx_version": ox.__version__,
        "bbox_west_south_east_north": BBOX,
        "network_type": "drive",
        "nodes": graph.number_of_nodes(),
        "directed_edges": graph.number_of_edges(),
        "graphml": GRAPH_FILE.name,
        "graphml_md5": md5(GRAPH_FILE),
        "downloaded": time.strftime("%Y-%m-%d %H:%M:%S"),
        "seconds": round(time.time() - start, 1),
    }
    (OUT_DIR / "osm_report.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
