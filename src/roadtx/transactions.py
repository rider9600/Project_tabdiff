"""Turn matched routes into user traversal transactions (UTTs), as in Rathan, Reddy & Mondal (2022).

A route is a list of graph nodes in travel order; its directed edges are consecutive node pairs.

Backtracking rule (paper, Sect. 3.1 and 4.2): whenever the traversal reaches a node it has already
visited, the edges so far form one UTT, and the traversal continues from the preceding node as a new
UTT. Each UTT is therefore a simple path, so its order can be recovered by chaining its edges.
"""

from __future__ import annotations

from typing import Hashable, Iterable, Sequence

Edge = tuple[Hashable, Hashable]


def split_backtracking(nodes: Sequence[Hashable]) -> list[list[Edge]]:
    """Split one route into UTTs with the backtracking rule. Returns lists of directed edges."""
    utts: list[list[Edge]] = []
    current: list[Edge] = []
    visited: set[Hashable] = set()
    for k, node in enumerate(nodes):
        if k == 0:
            visited = {node}
            continue
        prev = nodes[k - 1]
        if node == prev:
            continue
        if node in visited:
            if current:
                utts.append(current)
            current, visited = [], {prev}
        current.append((prev, node))
        visited.add(node)
    if current:
        utts.append(current)
    return utts


def clip_runs(edges: Sequence[Edge], keep: set[Edge], min_edges: int = 2) -> list[list[Edge]]:
    """Cut a UTT into maximal runs of consecutive edges that are all in `keep`.

    Used to restrict transactions to an area or a column set without creating gaps: every run is
    still a contiguous simple path. Runs shorter than `min_edges` are dropped.
    """
    runs, current = [], []
    for e in edges:
        if e in keep:
            current.append(e)
        else:
            if len(current) >= min_edges:
                runs.append(current)
            current = []
    if len(current) >= min_edges:
        runs.append(current)
    return runs


def chain(edges: Iterable[Edge]) -> list[Hashable] | None:
    """Order a set of directed edges into one simple path; None if they do not form one.

    A valid transaction has exactly one start node (out-degree 1, in-degree 0), every node has
    in- and out-degree at most 1, and following the edges from the start visits every edge.
    """
    edges = list(edges)
    if not edges:
        return None
    out, indeg = {}, {}
    for u, v in edges:
        if u in out:                      # branch: two edges leave u
            return None
        out[u] = v
        indeg[v] = indeg.get(v, 0) + 1
        if indeg[v] > 1:                  # two edges enter v
            return None
    starts = [u for u in out if indeg.get(u, 0) == 0]
    if len(starts) != 1:                  # cycle (no start) or several pieces (gap)
        return None
    path = [starts[0]]
    while path[-1] in out and len(path) <= len(edges):
        path.append(out[path[-1]])
    return path if len(path) == len(edges) + 1 else None
