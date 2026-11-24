"""Graph-aware stochastic sampler for TabDiff (our extension, docs/project_plan.md section 5).

TabDiff's stochastic sampler (UnifiedCtimeDiffusion.edm_update) moves each decided categorical column
back to the mask state with a probability `move_chance` that is the same for every column ("churn"),
so the model can revise earlier decisions. Here, during sampling only, that probability is raised for
the road-segment columns that make the partly generated trip undrivable:

- branch: a node with two decided segments leaving it, or two entering it -> both segments;
- gap: the decided segments form several pieces -> the segments at piece ends, and the undecided-off
  segments that could join a piece end to a piece start (so the model can switch them on).

For a flagged column, move_chance becomes mc + (1 - mc) * strength. Unflagged columns keep TabDiff's
value, so strength = 0 gives back the original sampler. Training is unchanged; a trained model is reused.

install() patches UnifiedCtimeDiffusion in memory (no edit of baseline_tabdiff/).
"""

from __future__ import annotations

import pandas as pd
import torch

STATS = {"calls": 0, "flagged_share_sum": 0.0}


class _Graph:
    """Incidence of the segment columns, built once per device."""

    def __init__(self, edges: pd.DataFrame, device):
        nodes = pd.Index(pd.unique(pd.concat([edges["u"], edges["v"]])))
        self.u = torch.as_tensor(nodes.get_indexer(edges["u"]), device=device)
        self.v = torch.as_tensor(nodes.get_indexer(edges["v"]), device=device)
        k, n = len(edges), len(nodes)
        self.U = torch.zeros(k, n, device=device)
        self.V = torch.zeros(k, n, device=device)
        self.U[torch.arange(k, device=device), self.u] = 1.0
        self.V[torch.arange(k, device=device), self.v] = 1.0


def violations(x: torch.Tensor, one_index: torch.Tensor, mask_index: torch.Tensor, g: _Graph) -> torch.Tensor:
    """Boolean (batch, K): segment columns to re-mask with higher probability."""
    has_one = one_index >= 0
    on = (x == one_index) & has_one
    decided = x != mask_index
    onf = on.float()
    out = onf @ g.U                                   # decided-on segments leaving each node
    inn = onf @ g.V                                   # decided-on segments entering each node
    out_u, in_v = out[:, g.u], inn[:, g.v]
    branch = on & ((out_u > 1) | (in_v > 1))
    is_start = (out > 0) & (inn == 0)
    is_end = (inn > 0) & (out == 0)
    pieces = is_start.sum(dim=1, keepdim=True)
    multi = pieces > 1
    boundary = on & multi & ((inn[:, g.u] == 0) | (out[:, g.v] == 0))
    bridge = (~on) & decided & has_one & multi & (is_end[:, g.u] | is_start[:, g.v])
    return branch | boundary | bridge


def install(diffusion_cls, edges: pd.DataFrame, strength: float = 0.5) -> None:
    """Patch diffusion_cls so that sample() uses the graph-aware re-masking."""
    original_q_xt = diffusion_cls.q_xt
    original_sample = diffusion_cls.sample

    def q_xt(self, x, move_chance, strategy="hard"):
        if not getattr(self, "_tdr_active", False) or strength <= 0:
            return original_q_xt(self, x, move_chance, strategy)
        if getattr(self, "_tdr_graph", None) is None or self._tdr_graph.u.device != x.device:
            self._tdr_graph = _Graph(edges, x.device)
            # TabDiff's ordinal encoder sorts the values, so class 1 is "segment used" when a column
            # has two classes; a column never used in training has one class and can't be switched on.
            # mask_index holds the number of classes per column (the mask is the extra last class).
            n_classes = torch.as_tensor(self.mask_index, device=x.device)
            self._tdr_one = torch.where(n_classes == 2, 1, -1).to(x.device)
        flag = violations(x, self._tdr_one, self.mask_index.to(x.device), self._tdr_graph)
        mc = torch.broadcast_to(move_chance, x.shape).to(torch.float32)
        mc = mc + (1.0 - mc) * strength * flag.float()
        STATS["calls"] += 1
        STATS["flagged_share_sum"] += float(flag.float().mean())
        return original_q_xt(self, x, mc, strategy)

    def sample(self, num_samples):
        self._tdr_active = True
        try:
            return original_sample(self, num_samples)
        finally:
            self._tdr_active = False

    diffusion_cls.q_xt = q_xt
    diffusion_cls.sample = sample
