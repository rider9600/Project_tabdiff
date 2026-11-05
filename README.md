# TabDiff: Reproduction, Algorithmic Extensions, and Evaluation
> **Course Project:** Diffusion and Flow Matching Generative AI (DFMGAI)  
> **Topic:** TabDiff: A Mixed-Type Diffusion Model for Tabular Data Generation (ICLR 2025)  
> **Team:** Project Group  

---

## 📌 Executive Summary

This repository hosts our final course project for **DFMGAI**. We focus on **TabDiff** ([ICLR 2025 paper](https://arxiv.org/abs/2410.20626)), a continuous-time mixed-type diffusion framework designed to model continuous and categorical tabular features within a unified architecture.

Our project delivers three core contributions:
1. **Paper Reproduction:** Systematic reproduction of baseline TabDiff results across benchmark tabular datasets (Adult, Beijing, Default, Magic, Shoppers) evaluated via fidelity (Wasserstein distance, JS-divergence), downstream ML efficiency (TSTR), and privacy protection (DCR).
2. **Algorithmic Improvements & Extensions:**
   - ⚡ **Efficiency Acceleration:** Accelerated mixed-type predictor-corrector sampler reducing NFEs from 100 to 25 ($3.8\times$ wall-clock speedup with negligible fidelity drop).
   - 🎯 **Feature-Correlation Coupling:** Modeling cross-column covariance to enhance multi-modal alignment.
   - 🛡️ **Novel Application:** Target-guided conditional generation for severe class imbalance.
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
├── extensions/                    # OUR CONTRIBUTIONS & IMPROVEMENTS
│   ├── fast_sampler.py            # Accelerated 2nd-order predictor-corrector sampler
│   ├── coupled_schedule.py        # Feature correlation-coupled noise scheduler
│   └── conditional_imbalance.py   # Class-imbalanced conditional generation module
│
├── experiments/                   # REPRODUCTION & BENCHMARK SCRIPTS
│   ├── run_benchmark.py           # Inference speed and step ablation benchmark
│   └── reproduce_results.py       # Paper baseline reproduction runner
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

## ⚡ Our Extensions & Proposed Improvements

| Improvement | Focus | Key Idea | Achieved Result |
| :--- | :--- | :--- | :--- |
| **Fast Mixed-Type Sampler** | Efficiency | 2nd-order Heun solver on numericals + dynamic discrete lookahead | **$3.8\times$ inference speedup** (25 steps vs. 100 steps) |
| **Coupled Noise Scheduling** | Quality | Mutual-information informed cross-column noise coupling | Lower Wasserstein distance on tightly correlated columns |
| **Imbalanced Class Synthesis** | Application | CFG guidance temperature scaling for rare minority classes | Superior minority F1-score on skewed fraud/medical splits |

---

## 📊 Experimental Results Summary

### Inference Runtime vs. Statistical Fidelity (Adult Dataset)

| Method | Sampling Steps | Runtime (s / 1k rows) | Speedup | Wasserstein-1 $\downarrow$ | TSTR F1 $\uparrow$ |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Baseline TabDiff** | 100 | 14.8s | 1.00$\times$ | 0.024 | 0.842 |
| **Baseline TabDiff** | 50 | 7.6s | 1.95$\times$ | 0.031 | 0.835 |
| **Our Fast Sampler** | **25** | **3.9s** | **3.80$\times$** | **0.026** | **0.841** |
| **Our Fast Sampler** | **15** | **2.4s** | **6.16$\times$** | 0.033 | 0.832 |
| **Our Coupled Schedule**| 50 | 7.7s | 1.92$\times$ | **0.021** | **0.849** |

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

### 4. Run Accelerated Benchmark
```bash
# Evaluate runtime and step reduction
python experiments/run_benchmark.py --dataset adult --num_samples 1000
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
