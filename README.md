# TabDiff: a Multi-Modal Diffusion Model for Tabular Data Generation

<p align="center">
  <a href="https://github.com/MinkaiXu/TabDiff/blob/main/LICENSE">
    <img alt="MIT License" src="https://img.shields.io/badge/License-MIT-yellow.svg">
  </a>
  <!-- <a href="">
    <img alt="Openreview" src="">
  </a> -->
  <a href="https://arxiv.org/abs/2410.20626">
    <img alt="Paper URL" src="https://img.shields.io/badge/cs.LG-2410.20626-B31B1B.svg">
  </a>
</p>

<div align="center">
  <img src="images/tabdiff_demo.gif" alt="Model Logo" width="800" style="margin-left:'auto' margin-right:'auto' display:'block'"/>
  <p><em>Figure 1: Visualing the generative process of TabDiff. A high-quality version of this video can be found at <a href="images/tabdiff_demo.mp4" download>tabdiff_demo.mp4</a></em></p>
</div>

This repository provides the official implementation of the paper "TabDiff: a Multi-Modal Diffusion Model for Tabular Data Generation".

## Latest Update

- [2025.01]：Our code is finally released!

## Introduction

<div align="center">
  <img src="images/tabdiff_flowchart.jpg" alt="Model Logo" width="800" style="margin-left:'auto' margin-right:'auto' display:'block'"/>
  <p><em>Figure 2: The high-level schema of TabDiff</a></em></p>
</div>
TabDiff is a unified diffusion framework designed to model all muti-modal distributions of tabular data in a single model. Its key innovations include:  

1) Framing the joint diffusion process in continuous time,
2) A feature-wised learnable diffusion process that offsets the heterogeneity across different feature distributions,
3) Classifier-free guidance conditional generation for missing column value imputation. 

The schema of TabDiff is presented in the figure above. For more details, please refer to [our paper](https://arxiv.org/abs/2410.20626).


