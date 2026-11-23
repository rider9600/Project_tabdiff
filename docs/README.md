# Documents

| Item | Contents |
| :--- | :--- |
| [`project_plan.md`](project_plan.md) | **Current project plan:** TabDiff on road-traversal transactions (T-Drive), evaluation and graph-aware sampler |
| [`paper/`](paper/) | `TabDiff_ICLR2025.pdf`, the original paper: *TabDiff: a Mixed-type Diffusion Model for Tabular Data Generation* (ICLR 2025, [arXiv:2410.20626](https://arxiv.org/abs/2410.20626)) |
| [`presentations/`](presentations/) | `Initial_Presentation.pptx` (initial project presentation), `TabDiff_Mixed-Type_Diffusion.pptx` (paper overview deck), `beamer/` (LaTeX Beamer source of the final evaluation deck) |
| [`report/`](report/) | `main.tex`, the LaTeX source of the project report |

`references/` (local only, not in Git) holds paywalled reference papers such as Rathan, Reddy & Mondal (2022).

To build the LaTeX documents:

```bash
cd docs/presentations/beamer && pdflatex presentation.tex
cd docs/report && pdflatex main.tex
```
