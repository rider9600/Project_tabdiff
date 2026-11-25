# Results: TabDiff on T-Drive road-traversal transactions

Table `tdrive_k300`: 4 km window in Beijing, 300 directed road segments, 42,705 transactions split by
taxi (train 29,378 / val 4,566 / test 8,761). TabDiff trained for 2,000 epochs (17.85 GPU hours on one
RTX 2080 Ti). Checkpoint and sampler settings were chosen on the validation split only; the numbers
below are on the test split (8,761 rows per table). TabDiff rows are means over 3 sampling seeds; the
seed-to-seed spread is small (see `evaluation.json`).

## Choosing the checkpoint and the sampler (validation)

| Checkpoint | Default: segments/row | Default: drivable | Graph-aware 0.5: segments/row | Graph-aware 0.5: drivable |
|---|---|---|---|---|
| 500 | 3.60 | 59% | 1.98 | 94% |
| 750 | 3.85 | 60% | 2.01 | 94% |
| 1000 to 2000 | 4.28 to 4.38 | 6% | about 0.80 (25% empty) | 72% |

Real validation rows have 4.33 segments. After epoch 750, the default sampler keeps the per-segment
frequencies (busy-road Spearman about 0.81) but loses the joint structure (91% of rows have gaps).
Graph-aware strength at epoch 750: 0.1 gives 2.56 segments and 88% drivable non-empty rows; 0.25 gives 2.20 and
94%; 0.5 gives 2.01 and 97%. Chosen: epoch 750, default and graph-aware 0.1.

## Test results

| Method | Drivable rows | Rows with gaps | Segments / row | Busy roads: Spearman | Busy roads: top-25 overlap | Frequent itemsets: Jaccard | Maximal patterns contiguous | Popular paths: Kendall τ (no minF) | Exact copies of train rows |
|---|---|---|---|---|---|---|---|---|---|
| Real test (reference) | 100% | 0% | 4.26 | 0.87 | 0.80 | 0.60 | 100% | 0.92 | 98.7% |
| Independent baseline | 5.8% | 92.2% | 4.28 | 0.91 | 0.83 | 0.00 | n/a | 0.50 | 0.1% |
| Markov baseline | 100% | 0% | 4.31 | 0.92 | 0.85 | 0.51 | 94% | 0.74 | 92.8% |
| TabDiff, default sampler | 61% | 37% | 3.86 | 0.81 | 0.48 | 0.10 | 44% | 0.85 | 47% |
| TabDiff, graph-aware 0.1 | 87% | 12% | 2.57 | 0.52 | 0.23 | 0.03 | 100% | 0.50 | 62% |

## Reading

- TabDiff keeps which roads are busy (Spearman 0.81) and the row length, but only 61% of its rows are
  drivable routes, and it recovers few frequent patterns (Jaccard 0.10 against 0.60 for real data).
- The graph-aware sampler raises drivable rows from 61% to 87% and makes every maximal pattern
  contiguous, but it shortens rows (2.57 segments) and loses busy-road agreement. It trades fidelity for
  validity.
- A first-order Markov chain on the road graph beats TabDiff on every fidelity measure here. It is valid by
  construction and copies most training rows, so it is a strong but low-privacy reference.
- Exact copies are high even for real test data (98.7%): in a 4 km window many trips use the same few
  segments, so exact-copy share must be read against that reference. DCR (distance to closest record):
  about 3.5% of TabDiff rows are closer to train than to test, against 0% for real test rows.

## Limitations of the evaluation

- Popular paths: with minF = 423, every candidate path in the window has at least one segment below minF,
  so Reddy et al.'s ω is 0 for all of them. We also report ω without the minF rule. The 26 queries cluster
  around 3 destinations (the window offers few route choices), and precision@3 is 1.0 by construction
  (3 candidates per query).
- One window, one dataset, one training run.
