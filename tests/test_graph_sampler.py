"""Tests for the graph-aware re-masking rule (needs torch; skipped where torch is not installed)."""

import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

try:
    import torch
    from roadtx.graph_sampler import _Graph, violations
except ImportError:  # the laptop's data-prep env has no torch
    torch = None

# Segments: e0 1->2, e1 2->3, e2 3->4, e3 2->5. Classes: 0 = off, 1 = on, 2 = mask.
EDGES = pd.DataFrame({"column": ["e0", "e1", "e2", "e3"], "u": [1, 2, 3, 2], "v": [2, 3, 4, 5]})


@unittest.skipIf(torch is None, "torch not installed")
class ViolationsTest(unittest.TestCase):
    def setUp(self):
        self.g = _Graph(EDGES, "cpu")
        self.one = torch.tensor([1, 1, 1, 1])
        self.mask = torch.tensor([2, 2, 2, 2])

    def flags(self, row):
        return violations(torch.tensor([row]), self.one, self.mask, self.g)[0].tolist()

    def test_valid_path_has_no_flags(self):
        self.assertEqual(self.flags([1, 1, 1, 0]), [False, False, False, False])

    def test_gap_flags_piece_ends_and_bridges(self):
        # e0 and e2 on, e1 off: two pieces. e0 and e2 are piece ends; e1 (and e3) leave the end node 2.
        self.assertEqual(self.flags([1, 0, 1, 0]), [True, True, True, True])

    def test_branch_flags_both_segments(self):
        # e1 and e3 both leave node 2.
        self.assertEqual(self.flags([1, 1, 0, 1]), [False, True, False, True])

    def test_masked_columns_are_not_bridges(self):
        self.assertEqual(self.flags([1, 2, 1, 2]), [True, False, True, False])


if __name__ == "__main__":
    unittest.main()
