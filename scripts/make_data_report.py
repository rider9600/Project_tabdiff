"""Write data_clean/data_report.json: the MD5 of every file uploaded to Ada (rules/03, runbook step 1).

    .venv/Scripts/python scripts/make_data_report.py

Each Ada job recomputes these MD5s on the compute node and stops on any mismatch.
"""

import hashlib
import json
import shutil
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT / "data_clean"
GRAPH_SRC = ROOT / "data_raw" / "osm" / "beijing_5th_ring_drive.graphml"
FILES = ["tdrive_points.parquet", "beijing_5th_ring_drive.graphml"]


def md5(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    shutil.copy2(GRAPH_SRC, CLEAN / GRAPH_SRC.name)   # the upload takes files from data_clean/ only
    report = {"created": time.strftime("%Y-%m-%d %H:%M:%S"),
              "files": {name: {"bytes": (CLEAN / name).stat().st_size, "md5": md5(CLEAN / name)} for name in FILES}}
    (CLEAN / "data_report.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
