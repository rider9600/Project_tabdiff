# Hypotheses (DRAFT, not yet registered)

**To register with the user's agreement before the main runs (E3).** The thresholds are proposals.
Changes after registration are logged as decisions.

| # | Hypothesis | Test | Margin / threshold |
|---|---|---|---|
| H1 | TabDiff with the default sampler generates mostly valid trips | % of generated transactions that chain into one simple path | Draft: report the value; compare with independent sampling and the Markov chain |
| H2 | The graph-aware sampler increases the share of valid trips over the default sampler | Paired by sampling seed: difference in % valid, 95% t-interval | Draft: an improvement of at least 5 percentage points counts as meaningful |
| H3 | The graph-aware sampler does not harm pattern fidelity | Frequent-itemset overlap (Jaccard), TOST equivalence | Draft: margin of 0.05 Jaccard |
| H4 | Synthetic data preserves the busy roads | Top-50 busiest-segment overlap and Spearman correlation of per-segment counts, against real vs real | Draft: report against the real-vs-real reference |
| H5 | Synthetic data preserves the top-k popular paths | Kendall's tau and precision@k over about 10 source-destination queries | Draft: report against the real-vs-real reference |

Note: with 3 sampling seeds from one trained model, these tests measure sampling variance only
(decision 10); the report states this.
