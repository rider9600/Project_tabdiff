"""Baseline generators for road-traversal transactions (docs/project_plan.md, section 6).

- independent: every segment column drawn on its own with its training frequency (lower bound: it
  ignores all dependence between segments).
- markov: first-order Markov chain over segments, fitted on the ordered training transactions: a start
  segment, then the next segment given the current one, or stop. Walks never revisit a node, as real
  transactions are simple paths (backtracking rule).

Both return a table in the same format as the real data (segment columns "0"/"1" plus length_km).
"""

from __future__ import annotations

from collections import Counter, defaultdict

import numpy as np
import pandas as pd


def _table(rows: list[list[int]], edges: pd.DataFrame) -> pd.DataFrame:
    names = list(edges["column"])
    arr = np.zeros((len(rows), len(names)), dtype=np.int8)
    for i, r in enumerate(rows):
        arr[i, r] = 1
    df = pd.DataFrame(arr.astype(str), columns=names)
    df["length_km"] = np.round(arr @ edges["length_m"].to_numpy() / 1000.0, 4)
    return df


def independent(train: pd.DataFrame, edges: pd.DataFrame, n: int, seed: int = 0) -> pd.DataFrame:
    from .evaluate import to_bool

    p = to_bool(train).mean().reindex(edges["column"]).to_numpy()
    rng = np.random.default_rng(seed)
    draws = rng.random((n, len(p))) < p
    return _table([list(np.flatnonzero(r)) for r in draws], edges)


def markov(train_transactions: list[list[int]], edges: pd.DataFrame, n: int, seed: int = 0,
           max_len: int = 200) -> pd.DataFrame:
    """train_transactions: ordered column indices of each real training transaction."""
    starts = Counter(t[0] for t in train_transactions if t)
    nxt = defaultdict(Counter)
    for t in train_transactions:
        for a, b in zip(t[:-1], t[1:]):
            nxt[a][b] += 1
        if t:
            nxt[t[-1]][-1] += 1                      # -1 = stop
    u, v = edges["u"].to_numpy(), edges["v"].to_numpy()
    rng = np.random.default_rng(seed)
    s_keys = np.array(list(starts))
    s_p = np.array([starts[k] for k in s_keys], dtype=float)
    s_p /= s_p.sum()
    rows = []
    for _ in range(n):
        cur = int(rng.choice(s_keys, p=s_p))
        walk, seen = [cur], {u[cur], v[cur]}
        while len(walk) < max_len:
            options = nxt.get(cur)
            if not options:
                break
            keys = np.array(list(options))
            p = np.array([options[k] for k in keys], dtype=float)
            p /= p.sum()
            step = int(rng.choice(keys, p=p))
            if step == -1 or v[step] in seen:      # stop, or the walk would revisit a node
                break
            walk.append(step)
            seen.add(v[step])
            cur = step
        rows.append(walk)
    return _table(rows, edges)
