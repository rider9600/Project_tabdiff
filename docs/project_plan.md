# Project Plan: Generating Road-Traversal Transactions with TabDiff

**Course:** Diffusion & Flow Matching Generative AI (DFMGAI)
**Base papers:**
- Shi et al., *TabDiff: a Mixed-type Diffusion Model for Tabular Data Generation*, ICLR 2025
- Rathan, Reddy & Mondal, *A framework for discovering popular paths using transactional modeling and pattern mining*, Distributed and Parallel Databases 40:109–133, 2022

---

## 1. Idea in one paragraph

Rathan, Reddy & Mondal (2022) convert road-network data (graph data) into **transactional data**, so that frequent pattern mining can be used to find popular paths. They model each vehicle trip as a market-basket transaction whose items are the road segments travelled. Once trips are transactions, they become **tabular data**, the input TabDiff is designed for. We train TabDiff on these transactions to generate **synthetic road traversals**. We then decode them back into routes on the road graph and test whether the synthetic data preserves:
1. drivable trips,
2. the busy roads,
3. the frequent patterns,
4. the popular paths that the Reddy et al. method finds in the real data.

We also extend TabDiff's stochastic sampler so that it uses the road graph to correct invalid routes during generation.

## 2. Research questions

- **RQ1.** Can a tabular diffusion model generate road-traversal transactions that are *valid*, meaning each generated trip is one drivable route?
- **RQ2.** Does the synthetic data preserve the **busy roads**, **frequent patterns** and **top-k popular paths** found by the Reddy et al. method on real data?
- **RQ3.** Does a **graph-aware stochastic sampler** improve validity and pattern fidelity over TabDiff's default sampler, without retraining?

## 3. Data and transactional modelling (following Reddy et al.)

**Dataset:** T-Drive (Microsoft Research). GPS trajectories of 10,357 Beijing taxis, 2–8 February 2008, ~15M points, average sampling interval ~177 s. It's one of the two datasets used by Reddy et al. We use a single dataset because of time and compute constraints (see §7).

**Pipeline:**
1. **Road graph:** Beijing road network from OpenStreetMap via OSMnx. Nodes are intersections; directed edges are road segments with lengths.
2. **Map-matching:** each trajectory is matched onto the road graph (GraphHopper, as in the paper), giving a sequence of directed edge IDs: a *user traversal* (UT).
3. **Transactions:** each UT is split into *user traversal transactions* (UTTs) with the **backtracking** rule: whenever a node is revisited, the edges so far form one UTT. Each UTT is therefore a simple path.
4. **Area:** experiments use one area of Beijing, chosen after map-matching so that **≥ 20,000 transactions** remain. If no area is large enough, we keep the whole region and restrict the columns to the most-travelled road segments.

**Encoding (dimensions and measures):**

| Role | What it is |
| :--- | :--- |
| Row (grain) | One transaction (UTT) |
| Dimension | Directed road segment (edge ID); one binary column per segment |
| Per-row measure | Presence (1 = segment travelled in this transaction) |
| Aggregated measure | Support: number of transactions containing an edge combination |
| Derived measures | Edge frequency RF(e), coverage counts Q(p,k), popularity score ω(p) |

Because items are *directed* edges and each transaction is a simple path, a transaction can be chained back into an ordered route. Time of day is not modelled, as in Reddy et al.

## 4. Model

**Base model:** TabDiff, unchanged, trained on the binary transaction table. Each road-segment column is a categorical (binary) feature handled by TabDiff's masked discrete diffusion.

**Training:**
- At most 8,000 epochs (the TabDiff default), with **quality-based early stopping**.
- Every 500 epochs, generate ~2,000 trips and measure path validity and pattern overlap on a validation split. Stop after 3 checks without improvement, and keep the best checkpoint.
- One training run. Results are averaged over **3 sampling seeds**.

## 5. Our extension: graph-aware stochastic sampler

TabDiff's stochastic sampler re-masks already-decided categorical columns at each step **uniformly at random**, so the model can reconsider earlier decisions. We make this correction **targeted**:
1. At each reverse step, decode the partially generated trip on the road graph.
2. Find the road segments that cause violations: **gaps** (unconnected pieces), **branches** (two segments leaving the same node) and **cycles**.
3. Re-mask those segments with higher probability and leave consistent segments untouched.

This combines TabDiff's error-correcting stochastic sampling with the road graph from Reddy et al. Only the sampler changes, so it reuses the trained model.

## 6. Evaluation

Synthetic and real data have the same number of rows. Patterns are mined with FP-Growth at a single threshold **minF**, set once on the real training data to the **third quartile of single-edge support**. It's lowered (e.g. to the median) if that yields fewer than ~100 multi-edge patterns, and the same absolute value is used for every dataset.

| Level | Question | Metrics |
| :--- | :--- | :--- |
| **Trips** | Is each generated trip drivable? | % valid trips (one connected simple path); counts of gaps, branches and cycles; trip-length and detour-ratio distributions vs real |
| **Busy roads** | Same busy road segments? | Top-k busiest-segment overlap; correlation of per-segment counts; real vs synthetic heat maps |
| **Patterns** | Same frequent combinations? | Overlap of frequent itemsets and support error; **contiguity rate** of maximal frequent patterns (contiguous stretches vs detour-style), real vs synthetic; plausibility of synthetic detours on the road graph |
| **Popular paths** | Same popular routes? | Reddy et al.'s popularity score ω(p) = Σₖ Q(p,k)·W(k), with partial coverage and the per-edge minF condition. Top-k ranking agreement (precision@k, Kendall's τ) for ~10 source–destination queries with δ = 0.2. |
| **Privacy** | Are real trips copied? | % of synthetic trips identical to a training trip; DCR |

**Reference points and baselines:**
- **Real vs real:** held-out 20% of real transactions (the best achievable score)
- **Independent sampling:** each segment drawn from its marginal (lower bound)
- **First-order Markov chain:** random walks using real transition probabilities (a strong, simple trajectory baseline)
- **TabDiff + default sampler** vs **TabDiff + graph-aware sampler (ours)**

## 7. Scope and limitations

- **One dataset (T-Drive) and one area of Beijing**, because of time and compute constraints. Generalisation to other cities is future work.
- **One training run;** variance is estimated over sampling seeds only.
- **One support threshold;** no sensitivity study.
- **Not modelled:** time of day, and order across transactions (both, as in Reddy et al.).
- **Map-matching quality:** T-Drive is sparsely sampled, so map-matching fills in segments between GPS points. Fallback if that fails: Geolife, the paper's other dataset.

## 8. Timeline (about 8–10 working days)

| Phase | Work | Time |
| :--- | :--- | :--- |
| 1 | Road graph, map-matching, transactions, area selection, TabDiff dataset | 2–3 days |
| 2 | Reddy et al. pipeline (FP-Growth, popularity, top-k), evaluation suite, baselines | 2 days (during training) |
| 3 | Pilot run + one full TabDiff training run | 1–2 days |
| 4 | Graph-aware sampler + comparison | 2–3 days |
| 5 | Report and presentation | 2 days |

## 9. Deliverables

- Code: data pipeline, evaluation suite, baselines, graph-aware sampler (in this repository)
- Results: metrics tables and real vs synthetic heat maps
- Final report and presentation
