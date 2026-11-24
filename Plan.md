# Plan

Last updated: 23 November 2026 (first version, from the agreed direction)

The full, public version of the plan is [docs/project_plan.md](docs/project_plan.md). It is pushed so
the professor and teammates can read it. This file holds only what is internal: the compute plan and
pointers. The two must not contradict each other: change the public plan when a decision changes it.

## 1. Problem and question

See docs/project_plan.md, sections 1 and 2 (RQ1 validity, RQ2 busy roads, patterns and popular paths,
RQ3 the graph-aware sampler).

## 2. Data

T-Drive, one area of Beijing with at least 20,000 transactions (decisions 2 and 6). Details in DATA.md.

## 3. Method

TabDiff unchanged for training; graph-aware stochastic sampler at sampling time (decision 12). See
docs/project_plan.md sections 4 and 5.

## 4. Experiments

GPU hours are placeholders until the benchmark job measures speed on the RTX 2080 Ti.

| # | Experiment | Runs | Predicted GPU h |
|---|---|---|---|
| E0 | Environment job (venv, imports, tests) | 1 | 0.2 |
| E1 | Benchmark: epochs per hour and memory on the transaction table; check exact resume | 1 | 0.5 |
| E2 | Pilot: short TabDiff run (about 1,000 epochs) with quality checks | 1 | to measure |
| E3 | Main TabDiff training: up to 8,000 epochs, quality-based early stopping (decision 9) | 1 (decision 10) | to measure; split into 6 h jobs with resume |
| E4 | Sampling: default sampler vs graph-aware sampler, 3 sampling seeds each, plus no-churn | 9 sampling runs | small |
| E5 | Baselines: independent sampling, Markov chain (CPU, laptop or Ada) | 2 x 3 seeds | CPU |

## 5. Analysis and statistics

Evaluation levels in docs/project_plan.md section 6: trip validity, busy roads, patterns (including
maximal-pattern contiguity), popular paths, privacy. Real vs real (held-out 20%) as the reference.
Mean and spread over 3 sampling seeds. One training run only, so variance across training seeds is not
measured: this is stated as a limitation (decision 10).

## 6. Timeline (targets, not deadlines)

About 8 to 10 working days from the start of data work (docs/project_plan.md section 8). GPU budget on
Ada: _to ask the user_.

## 7. Possible comparisons (under discussion)

- **Coordinate encoding vs edge encoding.** Instead of road-segment transactions, give TabDiff each
  trip as GPS coordinates resampled to a fixed number of points (e.g. 16 points = 32 numeric columns),
  map-match the generated coordinates, and apply the same evaluation. Related work: DiffTraj (Zhu et
  al., NeurIPS 2023) generates GPS trajectories with diffusion and a sequence network; Diff-RNTraj adds
  road-network constraints. Estimated cost: 1 to 2 h on Ada plus ~1 h map-matching, after the main run.

