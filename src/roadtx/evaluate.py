"""Evaluate synthetic road-traversal transactions against real ones (docs/project_plan.md, section 6).

A transaction table has one "0"/"1" column per road segment (e000, e001, ...) and a numeric target
length_km. `edges` is the edges.csv written by scripts/build_transactions.py (column, u, v, length_m).

Levels:
1. Trips: is each row one drivable simple path? (valid / gap / branch / cycle / empty) and does the
   generated length_km match the length of the generated segments?
2. Busy roads: per-segment use, top-k overlap and Spearman correlation.
3. Patterns: frequent itemsets (FP-Growth) at one absolute support threshold minF, overlap and support
   error; contiguity rate of maximal frequent itemsets (contiguous stretch vs detour style).
4. Popular paths: Rathan, Reddy & Mondal's popularity score with partial coverage and the per-edge
   minF condition, for fixed source-destination queries; ranking agreement with the real data.
5. Privacy: exact copies of training rows, and distance to closest record (train vs held-out test).
"""

from __future__ import annotations

import itertools
import os
from collections import Counter

import networkx as nx
import numpy as np
import pandas as pd
from mlxtend.frequent_patterns import fpgrowth
# Longest itemset mined (6 for T-Drive); can be set with ROADTX_MAX_LEN for tables with longer rows,
# where the number of frequent subsets would otherwise explode.
MAX_LEN = int(os.environ.get("ROADTX_MAX_LEN", "6"))
from scipy.stats import kendalltau, spearmanr

from .transactions import chain, classify


# ---------------------------------------------------------------- helpers

def segment_columns(df: pd.DataFrame) -> list[str]:
    return [c for c in df.columns if c.startswith("e") and c[1:].isdigit()]


def to_bool(df: pd.DataFrame) -> pd.DataFrame:
    """The segment columns as a boolean matrix (accepts "0"/"1" strings or numbers)."""
    cols = segment_columns(df)
    return df[cols].astype(str).apply(lambda s: s.str.strip().isin(["1", "1.0", "True"])).astype(bool)


def row_edges(b: pd.DataFrame, edges: pd.DataFrame) -> list[list[tuple]]:
    uv = list(zip(edges["u"], edges["v"]))
    pos = {c: i for i, c in enumerate(edges["column"])}
    idx = [pos[c] for c in b.columns]
    arr = b.to_numpy()
    return [[uv[idx[j]] for j in np.flatnonzero(r)] for r in arr]


# ---------------------------------------------------------------- 1. trips

def trip_validity(df: pd.DataFrame, edges: pd.DataFrame) -> dict:
    b = to_bool(df)
    rows = row_edges(b, edges)
    kinds = Counter(classify(r) for r in rows)
    n = max(len(rows), 1)
    out = {f"share_{k}": round(kinds.get(k, 0) / n, 4) for k in ("valid", "gap", "branch", "cycle", "empty")}
    out["rows"] = len(rows)
    out["segments_per_row_mean"] = round(float(b.sum(axis=1).mean()), 3) if len(b) else 0.0
    if "length_km" in df.columns:
        length = dict(zip(edges["column"], edges["length_m"]))
        implied = b.to_numpy() @ np.array([length[c] for c in b.columns]) / 1000.0
        gen = pd.to_numeric(df["length_km"], errors="coerce").to_numpy()
        out["length_km_mean_abs_error"] = round(float(np.nanmean(np.abs(gen - implied))), 4)
    return out


# ---------------------------------------------------------------- 2. busy roads

def busy_roads(real: pd.DataFrame, syn: pd.DataFrame, ks=(10, 25, 50)) -> dict:
    r, s = to_bool(real).mean(), to_bool(syn).mean()
    out = {"spearman_segment_use": round(float(spearmanr(r, s).statistic), 4)}
    for k in ks:
        top_r, top_s = set(r.nlargest(k).index), set(s.nlargest(k).index)
        out[f"top{k}_overlap"] = round(len(top_r & top_s) / k, 4)
    return out


# ---------------------------------------------------------------- 3. patterns

def min_support_count(real_train: pd.DataFrame, quantile: float = 0.75) -> int:
    """minF (decision 8): the given quantile of single-segment support counts in the real train data."""
    counts = to_bool(real_train).sum()
    return max(int(np.quantile(counts[counts > 0], quantile)), 2)


def frequent_itemsets(df: pd.DataFrame, min_count: int, max_len: int = MAX_LEN) -> dict[frozenset, float]:
    b = to_bool(df)
    if len(b) == 0:
        return {}
    fi = fpgrowth(b, min_support=min_count / len(b), use_colnames=True, max_len=max_len)
    return {frozenset(items): float(sup) for items, sup in zip(fi["itemsets"], fi["support"])}


def maximal(itemsets: dict[frozenset, float]) -> list[frozenset]:
    multi = sorted((s for s in itemsets if len(s) > 1), key=len, reverse=True)
    kept: list[frozenset] = []
    for s in multi:
        if not any(s < k for k in kept):
            kept.append(s)
    return kept


def contiguity_rate(sets: list[frozenset], edges: pd.DataFrame) -> float:
    uv = dict(zip(edges["column"], zip(edges["u"], edges["v"])))
    if not sets:
        return float("nan")
    return float(np.mean([chain([uv[c] for c in s]) is not None for s in sets]))


def pattern_fidelity(real: pd.DataFrame, syn: pd.DataFrame, edges: pd.DataFrame, min_count: int,
                     max_len: int = MAX_LEN) -> dict:
    """Compare frequent itemsets at the same absolute threshold. Real and synthetic should have the
    same number of rows; the count is rescaled if they do not."""
    syn_count = max(int(round(min_count * len(syn) / max(len(real), 1))), 2)
    fr = frequent_itemsets(real, min_count, max_len)
    fs = frequent_itemsets(syn, syn_count, max_len)
    mr = {k for k in fr if len(k) > 1}
    ms = {k for k in fs if len(k) > 1}
    common = mr & ms
    out = {
        "min_count": min_count,
        "multi_itemsets_real": len(mr), "multi_itemsets_syn": len(ms),
        "jaccard_multi_itemsets": round(len(common) / max(len(mr | ms), 1), 4),
        "recall_real_itemsets": round(len(common) / max(len(mr), 1), 4),
        "support_mean_abs_error_common": round(float(np.mean([abs(fr[k] - fs[k]) for k in common])), 5)
        if common else float("nan"),
    }
    max_r, max_s = maximal(fr), maximal(fs)
    out["maximal_real"], out["maximal_syn"] = len(max_r), len(max_s)
    out["contiguity_maximal_real"] = round(contiguity_rate(max_r, edges), 4)
    out["contiguity_maximal_syn"] = round(contiguity_rate(max_s, edges), 4)
    return out


# ---------------------------------------------------------------- 4. popular paths

def column_graph(edges: pd.DataFrame) -> nx.DiGraph:
    g = nx.DiGraph()
    for c, u, v, length in zip(edges["column"], edges["u"], edges["v"], edges["length_m"]):
        g.add_edge(u, v, column=c, length=float(length))
    return g


def candidate_paths(g: nx.DiGraph, s, t, delta: float = 0.2, cap: int = 30) -> list[list[str]]:
    """Paths from s to t no longer than (1 + delta) x the shortest (Reddy et al.), as column lists."""
    paths = []
    try:
        gen = nx.shortest_simple_paths(g, s, t, weight="length")
        shortest = None
        for nodes in gen:
            length = sum(g[a][b]["length"] for a, b in zip(nodes[:-1], nodes[1:]))
            shortest = shortest or length
            if length > (1 + delta) * shortest or len(paths) >= cap:
                break
            paths.append([g[a][b]["column"] for a, b in zip(nodes[:-1], nodes[1:])])
    except nx.NetworkXNoPath:
        return []
    return paths


def popularity(path: list[str], b: pd.DataFrame, min_count: int) -> float:
    """omega(p) = sum_k Q(p, k) W(k), W(k) = k(k+1) / (n(n+1)); 0 if any edge has RF(e) < minF."""
    sub = b[path].to_numpy()
    if (sub.sum(axis=0) < min_count).any():
        return 0.0
    n = len(path)
    k = sub.sum(axis=1)
    k = k[k > 0]
    return float(np.sum(k * (k + 1) / (n * (n + 1))))


def choose_queries(real_train: pd.DataFrame, edges: pd.DataFrame, n_queries: int = 10, seed: int = 0,
                   delta: float = 0.2, max_tries: int = 400) -> list[tuple]:
    """Source-destination pairs with at least 3 candidate paths, chosen once on real train data."""
    g = column_graph(edges)
    rng = np.random.default_rng(seed)
    # Enumerate every pair 3 to 30 segments apart with at least 3 candidate paths, then sample. Random
    # probing missed them: in a 300-segment window the graph is fragmented and such pairs are rare.
    pairs, seen = [], set()
    for s in sorted(g.nodes):
        for t, h in sorted(nx.single_source_shortest_path_length(g, s, cutoff=30).items()):
            cands = candidate_paths(g, s, t, delta) if h >= 3 else []
            key = frozenset(tuple(p) for p in cands)
            if len(cands) >= 3 and key not in seen:   # one query per distinct set of alternatives
                seen.add(key)
                pairs.append((s, t))
    if len(pairs) <= n_queries:
        return pairs
    return [pairs[i] for i in sorted(rng.choice(len(pairs), n_queries, replace=False))]


def popular_path_agreement(real: pd.DataFrame, syn: pd.DataFrame, edges: pd.DataFrame, queries, min_count: int,
                           delta: float = 0.2, top: int = 3) -> dict:
    g = column_graph(edges)
    br, bs = to_bool(real), to_bool(syn)
    syn_count = max(int(round(min_count * len(syn) / max(len(real), 1))), 2)
    out = {"queries": len(queries)}
    # "": Reddy et al.'s omega (0 if any edge is below minF); "_no_minf": the same score without that
    # rule, so rankings stay comparable when every candidate path has an edge below minF.
    for tag, mr, ms in (("", min_count, syn_count), ("_no_minf", 0, 0)):
        taus, precs, zero = [], [], 0
        for s, t in queries:
            cands = candidate_paths(g, s, t, delta)
            sr = [popularity(p, br, mr) for p in cands]
            ss = [popularity(p, bs, ms) for p in cands]
            zero += int(max(sr) == 0)
            if np.std(sr) > 0 and np.std(ss) > 0:
                taus.append(kendalltau(sr, ss).statistic)
            top_r = set(np.argsort(sr)[::-1][:top])
            top_s = set(np.argsort(ss)[::-1][:top])
            precs.append(len(top_r & top_s) / min(top, len(cands)))
        out[f"kendall_tau_mean{tag}"] = round(float(np.mean(taus)), 4) if taus else float("nan")
        out[f"queries_with_tau{tag}"] = len(taus)
        out[f"queries_all_zero_real{tag}"] = zero
        out[f"precision_at_{top}_mean{tag}"] = round(float(np.mean(precs)), 4) if precs else float("nan")
    return out


# ---------------------------------------------------------------- 5. privacy

def privacy(syn: pd.DataFrame, train: pd.DataFrame, test: pd.DataFrame, max_rows: int = 5000, seed: int = 0) -> dict:
    """Exact copies of train rows, and DCR: share of synthetic rows closer (Hamming) to train than to test.
    About 0.5 means no sign of memorisation when train and test are the same size."""
    rng = np.random.default_rng(seed)
    S = to_bool(syn).to_numpy()
    T = to_bool(train).to_numpy()
    H = to_bool(test).to_numpy()
    n = min(len(T), len(H))
    T = T[rng.choice(len(T), n, replace=False)]
    H = H[rng.choice(len(H), n, replace=False)]
    if len(S) > max_rows:
        S = S[rng.choice(len(S), max_rows, replace=False)]
    train_rows = {r.tobytes() for r in to_bool(train).to_numpy()}
    exact = float(np.mean([r.tobytes() in train_rows for r in S]))

    def nearest(A, B):
        A16, B16 = A.astype(np.int16), B.astype(np.int16)
        out = np.empty(len(A))
        for i in range(0, len(A), 512):
            a = A16[i:i + 512]
            d = a.sum(1)[:, None] + B16.sum(1)[None, :] - 2 * a @ B16.T
            out[i:i + 512] = d.min(1)
        return out

    dt, dh = nearest(S, T), nearest(S, H)
    return {"exact_copy_share": round(exact, 4), "dcr_closer_to_train_share": round(float(np.mean(dt < dh)), 4),
            "dcr_ties_share": round(float(np.mean(dt == dh)), 4)}


def evaluate_all(real_train: pd.DataFrame, real_test: pd.DataFrame, syn: pd.DataFrame, edges: pd.DataFrame,
                 min_count: int, queries) -> dict:
    """All levels for one synthetic table against the real data at the same size."""
    n = min(len(real_train), len(syn))
    ref = real_train.sample(n, random_state=0) if len(real_train) > n else real_train
    s = syn.sample(n, random_state=0) if len(syn) > n else syn
    return {
        "trips": trip_validity(s, edges),
        "busy_roads": busy_roads(ref, s),
        "patterns": pattern_fidelity(ref, s, edges, int(round(min_count * n / len(real_train)))),
        "popular_paths": popular_path_agreement(ref, s, edges, queries, int(round(min_count * n / len(real_train)))),
        "privacy": privacy(s, real_train, real_test),
    }


__all__ = [name for name in dir() if not name.startswith("_") and name not in {"itertools", "Counter"}]
