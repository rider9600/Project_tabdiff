"""Profile the raw T-Drive data before cleaning: counts, duplicates, invalid points, coverage, gaps.

    .venv/Scripts/python scripts/profile_tdrive.py

Reads data_raw/tdrive/release/taxi_log_2008_by_id/*.txt (one file per taxi; rows are
`taxi id, date time, longitude, latitude`). Writes data_raw/tdrive/profile_report.json and prints it.
The raw data is never written anywhere else (licence: no redistribution).
"""

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data_raw" / "tdrive" / "release" / "taxi_log_2008_by_id"
REPORT = ROOT / "data_raw" / "tdrive" / "profile_report.json"

# Beijing municipality (generous) and the 5th Ring Road box used for the road graph.
BEIJING = (115.4, 39.4, 117.5, 41.1)        # west, south, east, north
RING5 = (116.20, 39.75, 116.55, 40.03)


def in_box(lon, lat, box):
    w, s, e, n = box
    return (lon >= w) & (lon <= e) & (lat >= s) & (lat <= n)


def haversine_m(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(np.radians, (lon1, lat1, lon2, lat2))
    a = np.sin((lat2 - lat1) / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2
    return 6371000.0 * 2 * np.arcsin(np.sqrt(a))


def main() -> None:
    start = time.time()
    files = sorted(RAW_DIR.glob("*.txt"), key=lambda p: int(p.stem))
    frames, empty = [], 0
    for path in files:
        if path.stat().st_size == 0:
            empty += 1
            continue
        frames.append(pd.read_csv(path, header=None, names=["taxi", "t", "lon", "lat"]))
    df = pd.concat(frames, ignore_index=True)
    df["t"] = pd.to_datetime(df["t"], errors="coerce")

    rep = {"files": len(files), "empty_files": empty, "rows": int(len(df)), "taxis": int(df["taxi"].nunique())}
    rep["bad_timestamps"] = int(df["t"].isna().sum())
    rep["exact_duplicate_rows"] = int(df.duplicated().sum())
    rep["duplicate_taxi_time"] = int(df.duplicated(["taxi", "t"]).sum())
    rep["zero_coordinates"] = int(((df["lon"] == 0) | (df["lat"] == 0)).sum())
    rep["outside_beijing"] = int((~in_box(df["lon"], df["lat"], BEIJING)).sum())
    rep["inside_5th_ring_box"] = int(in_box(df["lon"], df["lat"], RING5).sum())
    rep["time_min"], rep["time_max"] = str(df["t"].min()), str(df["t"].max())

    d = df.dropna(subset=["t"]).drop_duplicates(["taxi", "t"]).sort_values(["taxi", "t"])
    same = d["taxi"].values[1:] == d["taxi"].values[:-1]
    dt = (d["t"].values[1:] - d["t"].values[:-1]).astype("timedelta64[s]").astype(float)[same]
    dist = haversine_m(d["lon"].values[:-1], d["lat"].values[:-1], d["lon"].values[1:], d["lat"].values[1:])[same]
    speed_kmh = np.where(dt > 0, dist / dt * 3.6, np.nan)
    q = [0.1, 0.25, 0.5, 0.75, 0.9, 0.99]
    rep["interval_s_quantiles"] = dict(zip(map(str, q), np.round(np.quantile(dt, q), 1).tolist()))
    rep["interval_s_mean"] = round(float(dt.mean()), 1)
    rep["distance_m_quantiles"] = dict(zip(map(str, q), np.round(np.quantile(dist, q), 1).tolist()))
    rep["gaps_over"] = {f"{m}min": int((dt > 60 * m).sum()) for m in (5, 10, 15, 30, 60)}
    rep["consecutive_pairs"] = int(same.sum())
    rep["speed_over_150kmh"] = int(np.nansum(speed_kmh > 150))
    rep["stationary_pairs_under_10m"] = int((dist < 10).sum())
    per_taxi = d.groupby("taxi").size()
    rep["points_per_taxi_quantiles"] = dict(zip(map(str, q), per_taxi.quantile(q).round().astype(int).tolist()))
    rep["seconds"] = round(time.time() - start, 1)
    REPORT.write_text(json.dumps(rep, indent=2))
    print(json.dumps(rep, indent=2))


if __name__ == "__main__":
    main()
