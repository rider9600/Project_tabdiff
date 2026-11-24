"""Tests for the transactional model (run: .venv/Scripts/python -m unittest discover -s tests)."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from roadtx.transactions import chain, clip_runs, split_backtracking  # noqa: E402


class BacktrackingTest(unittest.TestCase):
    def test_paper_figure_1_example(self):
        """Rathan, Reddy & Mondal (2022), Fig. 1 and Sect. 3.1: the backtracking method."""
        route = ["v1", "v2", "v3", "v4", "v5", "v6", "v7", "v6", "v5", "v8", "v9", "v1"]
        utts = split_backtracking(route)
        self.assertEqual(utts, [
            [("v1", "v2"), ("v2", "v3"), ("v3", "v4"), ("v4", "v5"), ("v5", "v6"), ("v6", "v7")],
            [("v7", "v6"), ("v6", "v5"), ("v5", "v8"), ("v8", "v9"), ("v9", "v1")],
        ])

    def test_every_utt_is_a_simple_path(self):
        route = [1, 2, 3, 2, 4, 5, 3, 6, 7, 6, 1]
        for utt in split_backtracking(route):
            self.assertIsNotNone(chain(utt))

    def test_repeated_node_is_ignored(self):
        self.assertEqual(split_backtracking([1, 1, 2, 2, 3]), [[(1, 2), (2, 3)]])


class ClipRunsTest(unittest.TestCase):
    def test_runs_have_no_gaps(self):
        edges = [(1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7)]
        keep = {(1, 2), (2, 3), (4, 5), (5, 6), (6, 7)}
        self.assertEqual(clip_runs(edges, keep), [[(1, 2), (2, 3)], [(4, 5), (5, 6), (6, 7)]])

    def test_short_runs_dropped(self):
        self.assertEqual(clip_runs([(1, 2), (2, 3), (3, 4)], {(1, 2), (3, 4)}), [])


class ChainTest(unittest.TestCase):
    def test_valid_path_any_order(self):
        self.assertEqual(chain([("C", "D"), ("A", "B"), ("B", "C")]), ["A", "B", "C", "D"])

    def test_gap(self):
        self.assertIsNone(chain([("A", "B"), ("C", "D")]))

    def test_branch(self):
        self.assertIsNone(chain([("A", "B"), ("B", "C"), ("B", "E")]))

    def test_cycle(self):
        self.assertIsNone(chain([("A", "B"), ("B", "C"), ("C", "A")]))

    def test_empty(self):
        self.assertIsNone(chain([]))


if __name__ == "__main__":
    unittest.main()
