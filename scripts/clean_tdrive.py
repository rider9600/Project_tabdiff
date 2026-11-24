"""Clean the raw T-Drive points and keep those inside the 5th Ring Road box.

    .venv/Scripts/python scripts/clean_tdrive.py

Steps (counts are written to data_clean/tdrive_clean_report.json):
1. Read every taxi file; drop empty files.
2. Drop rows with a repeated (taxi, time); keep the first.
3. Drop points with zero coordinates.
4. Drop GPS spikes: points whose speed from the previous point AND to the next point are both
   above 150 km/h (an isolated jump away and back). Repeated twice.
5. Keep points inside the 5th Ring Road box, the area of the road graph.

Output: data_clean/tdrive_points.parquet with columns taxi, t, lon, lat, sorted by taxi and time.
The data stays on this laptop and on the user's own Ada account (licence: no redistribution).
"""

import hashlib
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data_raw" / "tdrive" / "release" / "taxi_log_2008_by_id"
OUT_DIR = ROOT / "data_clean"
OUT_FILE = OUT_DIR / "tdrive_points.parquet"
RING5 = (116.20, 39.75, 116.55, 40.03)      # west, south, east, north (same as prepare_osm.py)
MAX_SPEED_KMH = 150.0


def haversine_m(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(np.radians, (lon1, lat1, lon2, lat2))
    a = np.sin((lat2 - lat1) / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2
    return 6371000.0 * 2 * np.arcsin(np.sqrt(a))


def drop_spikes(df: pd.DataFrame) -> pd.DataFrame:
    """Remove points with an impossible speed both into and out of them (same taxi)."""
    taxi, lon, lat = df["taxi"].values, df["lon"].values, df["lat"].values
    t = df["t"].values.astype("datetime64[s]").astype(np.int64)
    n = len(df)
    v_in = np.full(n, np.nan)
    same = taxi[1:] == taxi[:-1]
    dt = (t[1:] - t[:-1]).astype(float)
    dist = haversine_m(lon[:-1], lat[:-1], lon[1:], lat[1:])
    v = np.where(dt > 0, dist / np.maximum(dt, 1) * 3.6, np.inf)
    v_in[1:] = np.where(same, v, np.nan)
    v_out = np.full(n, np.nan)
    v_out[:-1] = np.where(same, v, np.nan)
    spike = (v_in > MAX_SPEED_KMH) & (v_out > MAX_SPEED_KMH)
    return df.loc[~spike].reset_index(drop=True)


def main() -> None:
    start = time.time()
    OUT_DIR.mkdir(exist_ok=True)
    files = sorted(RAW_DIR.glob("*.txt"), key=lambda p: int(p.stem))
    frames = [pd.read_csv(p, header=None, names=["taxi", "t", "lon", "lat"]) for p in files if p.stat().st_size > 0]
    df = pd.concat(frames, ignore_index=True)
    df["t"] = pd.to_datetime(df["t"])
    counts = {"raw_rows": len(df)}

    df = df.drop_duplicates(["taxi", "t"]).sort_values(["taxi", "t"]).reset_index(drop=True)
    counts["after_duplicates"] = len(df)
    df = df[(df["lon"] != 0) & (df["lat"] != 0)].reset_index(drop=True)
    counts["after_zero_coordinates"] = len(df)
    for i in (1, 2):
        df = drop_spikes(df)
        counts[f"after_spike_pass_{i}"] = len(df)
    w, s, e, n = RING5
    df = df[(df["lon"] >= w) & (df["lon"] <= e) & (df["lat"] >= s) & (df["lat"] <= n)].reset_index(drop=True)
    counts["after_5th_ring_box"] = len(df)
    counts["taxis"] = int(df["taxi"].nunique())

    df["taxi"] = df["taxi"].astype("int32")
    df[["lon", "lat"]] = df[["lon", "lat"]].astype("float64")
    df.to_parquet(OUT_FILE, index=False)
    md5 = hashlib.md5(OUT_FILE.read_bytes()).hexdigest()
    report = {**counts, "output": OUT_FILE.name, "output_md5": md5, "seconds": round(time.time() - start, 1)}
    (OUT_DIR / "tdrive_clean_report.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
