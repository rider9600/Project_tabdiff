"""Register a transaction table (from build_transactions.py) as a TabDiff dataset and preprocess it.

    python scripts/register_tabdiff_dataset.py --name tdrive_k300 [--python <interpreter>]

Copies data_clean/tabdiff/<name>/{train,val,test}.csv to baseline_tabdiff/data/<name>/, writes
baseline_tabdiff/data/Info/<name>.json, and runs TabDiff's own process_dataset.py, which creates the
.npy arrays, info.json and synthetic/<name>/real.csv that TabDiff's training and evaluation read.
Our train/val/test split (by taxi) is kept: process_dataset.py uses test_path and val_path as given.
None of these files are committed (data licence; see .gitignore).
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TABDIFF = ROOT / "baseline_tabdiff"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", default="tdrive_k300")
    ap.add_argument("--src", default="", help="folder with train/val/test.csv and info.json "
                                             "(default data_clean/tabdiff/<name>)")
    ap.add_argument("--python", default=sys.executable, help="interpreter that has TabDiff's packages")
    a = ap.parse_args()

    src = Path(a.src) if a.src else ROOT / "data_clean" / "tabdiff" / a.name
    dst = TABDIFF / "data" / a.name
    dst.mkdir(parents=True, exist_ok=True)
    for split in ("train", "val", "test"):
        shutil.copy2(src / f"{split}.csv", dst / f"{split}.csv")

    info = json.loads((src / "info.json").read_text())
    info.update({"name": a.name, "header": "infer",
                 "data_path": f"data/{a.name}/train.csv", "val_path": f"data/{a.name}/val.csv",
                 "test_path": f"data/{a.name}/test.csv"})
    (TABDIFF / "data" / "Info" / f"{a.name}.json").write_text(json.dumps(info, indent=4))

    subprocess.run([a.python, "process_dataset.py", "--dataname", a.name], cwd=TABDIFF, check=True)
    print(f"registered {a.name}: {sorted(p.name for p in dst.iterdir())}")


if __name__ == "__main__":
    main()
