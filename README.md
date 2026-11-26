# TabDiff: Reproduction, Algorithmic Extensions, and Evaluation
> **Course Project:** Diffusion and Flow Matching Generative AI (DFMGAI)  
> **Topic:** TabDiff: A Mixed-Type Diffusion Model for Tabular Data Generation (ICLR 2025)  
> **Team:** Project Group  

---

## 📌 Executive Summary

This repository hosts our final course project for **DFMGAI**. We focus on **TabDiff** ([ICLR 2025 paper](https://arxiv.org/abs/2410.20626)), a continuous-time mixed-type diffusion framework designed to model continuous and categorical tabular features within a unified architecture.

Our project delivers three core contributions:
1. **Paper Reproduction:** Systematic reproduction of baseline TabDiff results on the **Adult** benchmark dataset (8,000 epochs on Tesla T4 GPU), evaluated via fidelity (Shape, Trend, $\alpha$-Precision, $\beta$-Recall, C2ST), downstream ML efficiency (MLE / TSTR), and privacy protection (DCR).
2. **Proposed Extensions (Conceptual / Future Work):**
   - ⚡ **Fast Mixed-Type Sampling:** Conceptual 2nd-order predictor-corrector prototype in `extensions/fast_sampler.py` (not yet integrated or benchmarked).
   - 🎯 **Feature-Correlation Coupling & Imbalanced Synthesis:** Proposed future work directions (not yet implemented).
3. **Academic Deliverables:**
   - 📊 **LaTeX Presentation:** A 30-minute evaluation presentation in LaTeX Beamer (`presentation/presentation.tex`) adhering to the mandatory sections **(a)** through **(i)**.
   - 📝 **Project Report:** A comprehensive project report in LaTeX (`report/main.tex`).

---

## 📂 Repository Structure

To ensure maximum transparency for course professors and evaluators, the repository strictly demarcates the **original author codebase** from **our contributions**:

```
Project_tabdiff/
├── README.md                      # [THIS FILE] Master project guide for evaluators
│
├── baseline_tabdiff/              # ORIGINAL PAPER CODEBASE (untouched baseline)
│   ├── data/                      # Dataset specifications and column metadata
│   ├── eval/                      # Author evaluation scripts (Fidelity, MLE, DCR)
│   ├── images/                    # Paper illustrations and schematics
│   ├── src/                       # Data loaders, environment config, utilities
│   ├── tabdiff/                   # TabDiff core architecture, schedules, trainer
│   ├── download_dataset.py        # Dataset downloader
│   ├── process_dataset.py         # Tabular pre-processing pipeline
│   ├── main.py                    # Original training entrypoint
│   ├── tabdiff.yaml               # Conda environment specifications
│   └── README_ORIGINAL.md         # Original author README
│
├── extensions/                    # PROPOSED EXTENSIONS (CONCEPTUAL PROTOTYPES)
│   └── fast_sampler.py            # Prototype 2nd-order sampler (not yet integrated/benchmarked)
│
├── experiments/                   # REPRODUCTION & EVALUATION SCRIPTS
│   ├── eval_adult_full.py         # Full Adult evaluation suite (Shape, Trend, MLE, C2ST, alpha/beta, DCR)
│   └── TabDiff_Colab_Reproduction.ipynb # Colab / Kaggle reproduction notebook
│
├── results/                       # EXPERIMENTAL RESULTS & LOGS
│   ├── reproduction_logs/         # Raw logs from paper reproduction
│   └── efficiency_comparison/     # Speedup and quality trade-off tables
│
├── report/                        # PROJECT REPORT (LaTeX source)
│   └── main.tex                   # Complete project report with paper summary,
│                                  # reproduction results, and extensions
│
└── presentation/                  # FINAL EVALUATION SLIDES (LaTeX Beamer)
    └── presentation.tex           # Mandatory 30-min Beamer deck adhering to (a)-(i)
```

---

## 🔬 Paper Overview: Problem, Gaps & TabDiff Formulation

### 1. Problem Statement & Motivation
Tabular datasets power mission-critical applications (credit scoring, medical diagnostics, fraud detection). Synthesizing high-quality tabular data enables data sharing while preserving privacy and addressing extreme sample scarcity.

### 2. Gaps Addressed by TabDiff
- **Latent Continuous Models (e.g. TabSyn):** Suffer from quantization collapse and decoding loss when mapping discrete categories to continuous latent vectors.
- **Disjoint Continuous + Discrete Models (e.g. TabDDPM):** Suffer from unsynchronized time schedules and compounding discrete classification errors.
- **Uniform Schedules:** Fail to account for massive variance in column entropy and scale across tabular features.

### 3. TabDiff Core Contributions
- **Joint continuous-time framework:** Integrates VP-SDE for continuous features and categorical jump processes for discrete tokens directly in data space.
- **Feature-wise learnable schedules:** $\gamma_i(t) = \text{Softplus}(w_i t + b_i)$ learns optimal per-column diffusion rates.
- **Mixed-type stochastic sampler:** Uses stochastic churn to rectify discrete decoding mistakes.

---

## ⚡ Proposed Extensions & Future Work

> **Note:** The extensions below are proposed design directions and are **not implemented/benchmarked** in the current codebase.

| Extension | Focus | Proposed Idea | Status |
| :--- | :--- | :--- | :--- |
| **Fast Mixed-Type Sampler** | Efficiency | 2nd-order Heun solver on numericals + dynamic discrete lookahead (`extensions/fast_sampler.py`) | Conceptual prototype (not integrated) |
| **Coupled Noise Scheduling** | Quality | Mutual-information informed cross-column noise coupling | Future work (not implemented) |
| **Imbalanced Class Synthesis** | Application | CFG guidance temperature scaling for rare minority classes | Future work (not implemented) |

---

## 📊 Experimental Results Summary

### Adult Dataset Reproduction (8,000 Epochs) vs. TabDiff Paper

| Metric | TabDiff Paper (Adult) | Our Repro (8k) | Our Repro (8k EMA) |
| :--- | :---: | :---: | :---: |
| **Shape Error (%) $\downarrow$** | $0.63 \pm 0.05$ | **0.76%** (99.24%) | 0.80% (99.20%) |
| **Trend Error (%) $\downarrow$** | $1.49 \pm 0.16$ | **1.46%** (98.54%) | 1.60% (98.40%) |
| **Overall Density Score $\uparrow$** | -- | **98.89%** | 98.80% |
| **Data Validity (%) $\uparrow$** | 100.0% | **100.0%** | **100.0%** |
| **MLE (XGBoost AUROC) $\uparrow$** | $0.912 \pm 0.002$ | 0.9135 | **0.9138** |
| **MLE (XGBoost Binary F1) $\uparrow$** | -- | 0.6601 | **0.6774** |
| **MLE (XGBoost Accuracy) $\uparrow$** | -- | 0.8564 | **0.8616** |
| **C2ST (Logistic Detection) $\uparrow$** | 0.9950 | 0.9788 | **0.9850** |
| **$\alpha$-Precision (%) $\uparrow$** | $99.02 \pm 0.20$ | 98.80% | **99.09%** |
| **$\beta$-Recall (%) $\uparrow$** | $51.64 \pm 0.20$ | 54.40% | **54.81%** |
| **DCR (2:1 real/test split)** | $50.10\%$ (1:1 split) | 73.90% | 73.93% |

Full raw output is saved in [`results/adult_8000/all_results.json`](results/adult_8000/all_results.json).

---

## 🚀 Getting Started & Reproduction Guide

### 1. Environment Setup
```bash
# Clone the repository
git clone https://github.com/rider9600/Project_tabdiff.git
cd Project_tabdiff

# Create the conda environment
conda env create -f baseline_tabdiff/tabdiff.yaml
conda activate tabdiff
```

### 2. Download and Preprocess Datasets
```bash
# Download benchmark datasets
python baseline_tabdiff/download_dataset.py

# Preprocess dataset (e.g. Adult dataset)
python baseline_tabdiff/process_dataset.py adult
```

### 3. Run Baseline Training & Reproduction
```bash
# Train baseline TabDiff model
python baseline_tabdiff/main.py --dataname adult --method tabdiff
```

### 4. Run Full Adult Evaluation
```bash
# Evaluate Shape, Trend, MLE, C2ST, alpha-Precision, beta-Recall, and DCR
python experiments/eval_adult_full.py
```

---

## 🎓 Mandatory Evaluation Presentation Structure

The final 30-minute evaluation presentation is provided in LaTeX Beamer under [`presentation/presentation.tex`](presentation/presentation.tex). It strictly follows the mandatory nine-part syllabus:

- **(a) Problem Statement and Motivation:** Slides 3–4
- **(b) Gaps Addressed:** Slide 5
- **(c) Problem Formulation:** Slide 6
- **(d) Algorithm:** Slide 7
- **(e) Theory:** Slide 8
- **(f) Experiments & Reproduction:** Slide 9
- **(g) Extensions Done as Part of the Project:** Slide 10
- **(h) New Results and Algorithms:** Slide 11
- **(i) New Experimental Results:** Slide 12

To compile the presentation:
```bash
cd presentation
pdflatex presentation.tex
```

---

## 📄 Final Project Report

The complete report source is available in [`report/main.tex`](report/main.tex). It contains the paper summary, reproduction methodology, theoretical derivations, and extended empirical benchmarks.

To compile the report:
```bash
cd report
pdflatex main.tex
```

---

## 👥 Contributors
- **Course:** Diffusion & Flow Matching Generative AI (DFMGAI)
- **Repository:** [https://github.com/rider9600/Project_tabdiff](https://github.com/rider9600/Project_tabdiff)

