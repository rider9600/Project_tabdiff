"""Tests for the evaluation metrics (run: .venv/Scripts/python -m unittest discover -s tests)."""

import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from roadtx.evaluate import popularity, to_bool, trip_validity  # noqa: E402


def rows(spec):
    """spec: list of (count, set of columns) -> boolean table over e12, e23, e34."""
    cols = ["e12", "e23", "e34"]
    data = [[c in s for c in cols] for n, s in spec for _ in range(n)]
    return pd.DataFrame(data, columns=cols)


class PopularityTest(unittest.TestCase):
    def test_paper_worked_example_p1(self):
        """Rathan, Reddy & Mondal (2022), Sect. 4.3: omega(p1) = 100 for p1 = (e12, e23, e34).

        Table 2 gives counts of transactions covering exactly these edge combinations of p1:
        {e12} 40, {e23} 20, {e34} 30, {e12,e23} 30, {e12,e34} 20, {e23,e34} 40, {e12,e23,e34} 40,
        and W(k) = k(k+1) / (n(n+1)) with n = 3.
        """
        b = rows([(40, {"e12"}), (20, {"e23"}), (30, {"e34"}), (30, {"e12", "e23"}),
                  (20, {"e12", "e34"}), (40, {"e23", "e34"}), (40, {"e12", "e23", "e34"})])
        self.assertAlmostEqual(popularity(["e12", "e23", "e34"], b, min_count=1), 100.0)

    def test_min_count_zeroes_score(self):
        b = rows([(5, {"e12", "e23"}), (1, {"e34"})])
        self.assertEqual(popularity(["e12", "e23", "e34"], b, min_count=2), 0.0)


class TripValidityTest(unittest.TestCase):
    def test_shares(self):
        edges = pd.DataFrame({"column": ["e000", "e001", "e002"], "u": [1, 2, 9], "v": [2, 3, 8],
                              "length_m": [100.0, 200.0, 50.0]})
        df = pd.DataFrame({"e000": ["1", "1", "0"], "e001": ["1", "0", "0"], "e002": ["0", "1", "0"],
                           "length_km": [0.3, 0.15, 0.0]})
        out = trip_validity(df, edges)
        self.assertAlmostEqual(out["share_valid"], round(1 / 3, 4))
        self.assertAlmostEqual(out["share_gap"], round(1 / 3, 4))
        self.assertAlmostEqual(out["share_empty"], round(1 / 3, 4))
        self.assertAlmostEqual(out["length_km_mean_abs_error"], 0.0)

    def test_to_bool_accepts_strings(self):
        self.assertEqual(to_bool(pd.DataFrame({"e000": ["1", "0", "1.0"]}))["e000"].tolist(), [True, False, True])


if __name__ == "__main__":
    unittest.main()
