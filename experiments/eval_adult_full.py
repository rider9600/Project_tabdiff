"""
Full evaluation script for the 8,000-epoch TabDiff reproduction on the Adult dataset.
Computes all paper metrics on CPU without retraining:
  1. Fidelity: Shape, Trend, Overall (SDMetrics QualityReport)
  2. Detection: C2ST (SDMetrics LogisticDetection)
  3. Downstream Utility (MLE): Train on Synthetic, Test on Real (XGBClassifier AUC, F1, Acc)
  4. Sample-level Fidelity & Coverage: alpha-Precision and beta-Recall (Alaa et al. 2022)
  5. Privacy: Distance to Closest Record (DCR) comparing synthetic->real vs synthetic->test
"""

import json
import os
import sys
from copy import deepcopy

import numpy as np
import pandas as pd
import torch
from scipy.spatial.distance import cdist
from sklearn.metrics import pairwise_distances
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sdmetrics.single_table import LogisticDetection

BASELINE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "baseline_tabdiff"))
sys.path.insert(0, BASELINE_DIR)

import eval.mle.mle as mle_mod
from tabdiff.metrics import TabMetrics, reorder


def compute_alpha_beta_naive(real_np: np.ndarray, syn_np: np.ndarray, n_steps: int = 30):
    """
    Compute naive alpha-Precision and beta-Recall (Alaa et al., ICML 2022),
    matching synthcity's AlphaPrecision naive implementation.
    """
    scaler = StandardScaler()
    real_scaled = scaler.fit_transform(real_np).astype(np.float32)
    syn_scaled = scaler.transform(syn_np).astype(np.float32)

    emb_center = np.mean(real_scaled, axis=0)
    alphas = np.linspace(0, 1, n_steps)

    dist_real_center = np.sqrt(np.sum((real_scaled - emb_center) ** 2, axis=1))
    dist_syn_center = np.sqrt(np.sum((syn_scaled - emb_center) ** 2, axis=1))

    real_th = torch.from_numpy(real_scaled)
    syn_th = torch.from_numpy(syn_scaled)

    # Fast batched L2 distances via torch.cdist (uses BLAS SGEMM on CPU)
    dist_real_to_syn_list = []
    rad_real_nn_list = []
    batch_size = 2048
    for i in range(0, len(real_th), batch_size):
        b = real_th[i:i + batch_size]
        d_rs = torch.cdist(b, syn_th, p=2.0).min(dim=1).values
        dist_real_to_syn_list.append(d_rs.numpy())

        d_rr = torch.cdist(b, real_th, p=2.0)
        # 2nd smallest is closest distinct neighbor
        top2 = torch.topk(d_rr, k=2, dim=1, largest=False).values[:, 1]
        rad_real_nn_list.append(top2.numpy())

    dist_real_to_syn = np.concatenate(dist_real_to_syn_list)
    rad_real_nn = np.concatenate(rad_real_nn_list)

    alpha_precision_curve = []
    beta_coverage_curve = []

    for alpha in alphas[1:-1]:
        r_alpha = np.quantile(dist_real_center, alpha)
        alpha_prec = np.mean(dist_syn_center <= r_alpha)
        alpha_precision_curve.append(alpha_prec)

        # Beta-recall: fraction of real points inside the alpha-support whose nearest syn point is within local real NN radius
        in_support = dist_real_center <= r_alpha
        if np.any(in_support):
            beta_rec = np.mean(dist_real_to_syn[in_support] <= rad_real_nn[in_support])
        else:
            beta_rec = 0.0
        beta_coverage_curve.append(beta_rec)

    alphas_eval = alphas[1:-1]
    delta_precision_alpha = 1.0 - 2.0 * np.sum(np.abs(alphas_eval - np.array(alpha_precision_curve))) * (alphas_eval[1] - alphas_eval[0])
    delta_coverage_beta = 1.0 - 2.0 * np.sum(np.abs(alphas_eval - np.array(beta_coverage_curve))) * (alphas_eval[1] - alphas_eval[0])
    return float(delta_precision_alpha), float(delta_coverage_beta)


def compute_dcr_fast(real_df: pd.DataFrame, syn_df: pd.DataFrame, test_df: pd.DataFrame, info: dict) -> float:
    """
    Exact L1 DCR metric from TabMetrics.evaluate_dcr using torch.cdist for fast CPU execution.
    """
    num_col_idx = list(info["num_col_idx"])
    cat_col_idx = list(info["cat_col_idx"])
    target_col_idx = list(info["target_col_idx"])
    if info["task_type"] == "regression":
        num_col_idx += target_col_idx
    else:
        cat_col_idx += target_col_idx

    real_cp = real_df.copy()
    syn_cp = syn_df.copy()
    test_cp = test_df.copy()
    real_cp.columns = list(range(len(real_cp.columns)))
    syn_cp.columns = list(range(len(real_cp.columns)))
    test_cp.columns = list(range(len(real_cp.columns)))

    num_ranges = np.array([real_cp[i].max() - real_cp[i].min() for i in num_col_idx], dtype=np.float32)

    encoder = OneHotEncoder(handle_unknown="ignore")
    cat_complete = np.concatenate([
        real_cp[cat_col_idx].to_numpy().astype(str),
        test_cp[cat_col_idx].to_numpy().astype(str),
    ], axis=0)
    encoder.fit(cat_complete)

    def encode_df(df):
        num_np = df[num_col_idx].to_numpy(dtype=np.float32) / num_ranges
        cat_oh = encoder.transform(df[cat_col_idx].to_numpy().astype(str)).toarray().astype(np.float32)
        return np.concatenate([num_np, cat_oh], axis=1)

    real_np = encode_df(real_cp)
    syn_np = encode_df(syn_cp)
    test_np = encode_df(test_cp)

    batch_size = 2048
    dcrs_real, dcrs_test = [], []
    for i in range(0, len(syn_np), batch_size):
        b = syn_np[i:i + batch_size]
        d_r = pairwise_distances(b, real_np, metric="manhattan", n_jobs=-1).min(axis=1)
        d_t = pairwise_distances(b, test_np, metric="manhattan", n_jobs=-1).min(axis=1)
        dcrs_real.append(d_r)
        dcrs_test.append(d_t)

    dcrs_real = np.concatenate(dcrs_real)
    dcrs_test = np.concatenate(dcrs_test)
    return float(np.mean(dcrs_real < dcrs_test))


def evaluate_checkpoint_samples(syn_path: str, info: dict, real_path: str, test_path: str):
    # Patch tree_method='hist' for CPU execution
    for task in mle_mod._MODELS:
        for spec in mle_mod._MODELS[task]:
            if "tree_method" in spec.get("kwargs", {}):
                spec["kwargs"]["tree_method"] = ["hist"]

    syn_df = pd.read_csv(syn_path)
    real_df = pd.read_csv(real_path)
    test_df = pd.read_csv(test_path)

    tm = TabMetrics(
        real_data_path=real_path,
        test_data_path=test_path,
        val_data_path=None,
        info=info,
        device="cpu",
        metric_list=["density", "mle"],
    )
    out_metrics, out_extras = tm.evaluate(syn_df)

    # C2ST (with string column names for sdmetrics 0.33 compatibility)
    info_c2st = deepcopy(info)
    info_c2st["metadata"]["columns"] = {int(k): v for k, v in info_c2st["metadata"]["columns"].items()}
    r_c = real_df.copy()
    s_c = syn_df.copy()
    r_c.columns = range(len(r_c.columns))
    s_c.columns = range(len(s_c.columns))
    new_real, new_syn, meta = reorder(r_c, s_c, info_c2st)
    new_real.columns = [str(c) for c in new_real.columns]
    new_syn.columns = [str(c) for c in new_syn.columns]
    meta["columns"] = {str(k): v for k, v in meta["columns"].items()}
    print("Evaluating C2ST...", flush=True)
    c2st = float(LogisticDetection.compute(real_data=new_real, synthetic_data=new_syn, metadata=meta))

    print("Evaluating DCR...", flush=True)
    dcr = compute_dcr_fast(real_df, syn_df, test_df, info)

    print("Evaluating alpha-Precision and beta-Recall...", flush=True)
    num_col_idx = list(info["num_col_idx"])
    cat_col_idx = list(info["cat_col_idx"]) + list(info["target_col_idx"])
    r_np = real_df.copy()
    s_np = syn_df.copy()
    r_np.columns = range(len(r_np.columns))
    s_np.columns = range(len(s_np.columns))
    enc = OneHotEncoder(handle_unknown="ignore")
    enc.fit(r_np[cat_col_idx].to_numpy().astype(str))
    real_feat = np.concatenate([
        r_np[num_col_idx].to_numpy(dtype=np.float32),
        enc.transform(r_np[cat_col_idx].to_numpy().astype(str)).toarray(),
    ], axis=1)
    syn_feat = np.concatenate([
        s_np[num_col_idx].to_numpy(dtype=np.float32),
        enc.transform(s_np[cat_col_idx].to_numpy().astype(str)).toarray(),
    ], axis=1)
    alpha_prec, beta_rec = compute_alpha_beta_naive(real_feat, syn_feat)

    xgb_auroc = float(out_metrics["mle"])
    xgb_f1 = float(out_extras["mle"]["best_f1_scores"]["XGBClassifier"]["binary_f1"])
    xgb_acc = float(out_extras["mle"]["best_acc_scores"]["XGBClassifier"]["accuracy"])

    return {
        "density/Shape": float(out_metrics["density/Shape"]),
        "density/Trend": float(out_metrics["density/Trend"]),
        "density/Overall": float(out_metrics["density/Overall"]),
        "shape_error_pct": round((1.0 - float(out_metrics["density/Shape"])) * 100.0, 2),
        "trend_error_pct": round((1.0 - float(out_metrics["density/Trend"])) * 100.0, 2),
        "mle_auroc": round(xgb_auroc, 4),
        "mle_binary_f1": round(xgb_f1, 4),
        "mle_accuracy": round(xgb_acc, 4),
        "c2st": round(c2st, 4),
        "alpha_precision": round(alpha_prec, 4),
        "beta_recall": round(beta_rec, 4),
        "dcr": round(dcr, 4),
    }


if __name__ == "__main__":
    os.chdir(BASELINE_DIR)
    with open("data/adult/info.json", "r") as f:
        info = json.load(f)

    real_path = "synthetic/adult/real.csv"
    test_path = "synthetic/adult/test.csv"

    results = {}
    for name, rel_path in [
        ("epoch_8000", "tabdiff/result/adult/learnable_schedule/8000/samples.csv"),
        ("epoch_8000_ema", "tabdiff/result/adult/learnable_schedule/8000/ema/samples.csv"),
    ]:
        print(f"\nEvaluating {name} from {rel_path}...")
        results[name] = evaluate_checkpoint_samples(rel_path, info, real_path, test_path)
        print(json.dumps(results[name], indent=2))

    # Save combined JSON to results/adult_8000/all_results.json
    out_json_path = os.path.abspath(os.path.join("..", "results", "adult_8000", "all_results.json"))
    combined = dict(results["epoch_8000"])
    combined["ema"] = results["epoch_8000_ema"]
    combined["paper_tabdiff_adult_reference"] = {
        "shape_error_pct": 0.63,
        "trend_error_pct": 1.49,
        "mle_auroc": 0.912,
        "c2st": 0.9950,
        "alpha_precision": 0.9902,
        "beta_recall": 0.5164,
        "dcr": 0.5010,
    }
    with open(out_json_path, "w") as f:
        json.dump(combined, f, indent=2)
    print(f"\nSaved full evaluation results to {out_json_path}")
