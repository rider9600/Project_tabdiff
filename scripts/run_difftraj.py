"""Train (from scratch or from the authors' checkpoint) and sample DiffTraj on our exported trips.

    python scripts/run_difftraj.py train --name tdrive_k300 --exp scratch --epochs 200
    python scripts/run_difftraj.py train --name tdrive_k300 --exp finetune --epochs 50 --init external/DiffTraj/model.pt
    python scripts/run_difftraj.py sample --name tdrive_k300 --exp scratch --seed 10 --n 8761

Uses DiffTraj's own network (external/DiffTraj/utils/Traj_UNet.py: Guide_UNet), configuration
(utils/config.py) and sampler step (utils/utils.py: p_xt) unchanged; only the data paths, checkpoint
resume and output files are ours. Training follows the authors' main.py: AdamW lr 2e-4, batch 1024 (512 on our 11 GB GPU),
500-step linear beta schedule (1e-4 to 0.05), antithetic timesteps, MSE on the noise; the plain
(non-EMA) weights are saved, as in main.py. Sampling follows process/Traj_Generation.ipynb: DDIM,
100 steps, eta 0, guidance scale 3, attributes ("heads") drawn at random from the training split.

Checkpoints (Ada home is nearly full): during training, last.pt (weights + optimizer, for resume) is
overwritten every --check epochs in --work (node-local scratch on Ada, default the output folder); at the
end only the final weights are saved, out/difftraj/<name>/<exp>/model_final.pt (about 65 MB).
Samples: out/difftraj/<name>/<exp>/samples_s<seed>.npy, (n, 200, 2) in projected metres.
"""

import argparse
import json
import sys
import time
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import torch
import torch.nn.functional as F

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "external" / "DiffTraj"))
from utils.config import args as DT_ARGS  # noqa: E402
from utils.Traj_UNet import Guide_UNet  # noqa: E402
from utils.utils import p_xt  # noqa: E402


def config():
    return SimpleNamespace(**{k: SimpleNamespace(**v) for k, v in DT_ARGS.items()})


def train(a, cfg, data, out):
    work = Path(a.work) if a.work else out
    work.mkdir(parents=True, exist_ok=True)
    traj = torch.from_numpy(np.load(data / "traj_train.npy")).float().transpose(1, 2)   # (n, 2, L)
    head = torch.from_numpy(np.load(data / "head_train.npy")).float()
    assert traj.shape[2] == cfg.data.traj_length, "export length must match DiffTraj's traj_length"
    dl = torch.utils.data.DataLoader(torch.utils.data.TensorDataset(traj, head),
                                     batch_size=a.batch_size or cfg.training.batch_size, shuffle=True, num_workers=0)
    n_steps = cfg.diffusion.num_diffusion_timesteps
    beta = torch.linspace(cfg.diffusion.beta_start, cfg.diffusion.beta_end, n_steps).cuda()
    alpha_bar = torch.cumprod(1.0 - beta, dim=0)
    unet = Guide_UNet(cfg).cuda()
    optim = torch.optim.AdamW(unet.parameters(), lr=2e-4)
    start = 0
    resume = work / "last.pt"
    if resume.exists():
        ck = torch.load(resume, map_location="cuda")
        unet.load_state_dict(ck["model"])
        optim.load_state_dict(ck["optim"])
        start = ck["epoch"]
        print(f"=== resumed from {resume} (epoch {start})", flush=True)
    elif a.init:
        print(f"=== initialised from {a.init}: {unet.load_state_dict(torch.load(a.init, map_location='cuda'))}",
              flush=True)
    n_params = sum(p.numel() for p in unet.parameters())
    print(f"=== {n_params:,} parameters; {len(traj)} trips; epochs {start + 1}..{a.epochs}", flush=True)
    for epoch in range(start + 1, a.epochs + 1):
        t0, losses = time.time(), []
        for x0, h in dl:
            x0, h = x0.cuda(), h.cuda()
            t = torch.randint(0, n_steps, (len(x0) // 2 + 1,)).cuda()
            t = torch.cat([t, n_steps - t - 1], dim=0)[: len(x0)]
            ab = alpha_bar.gather(-1, t).reshape(-1, 1, 1)
            eps = torch.randn_like(x0)
            xt = ab.sqrt() * x0 + (1 - ab).sqrt() * eps
            loss = F.mse_loss(eps, unet(xt, t, h))
            optim.zero_grad()
            loss.backward()
            optim.step()
            losses.append(loss.item())
        print(f"epoch {epoch} loss {np.mean(losses):.5f} {time.time() - t0:.1f}s", flush=True)
        if epoch % a.check == 0 or epoch == a.epochs:
            torch.save({"model": unet.state_dict(), "optim": optim.state_dict(), "epoch": epoch}, work / "last.pt")
    torch.save({"model": unet.state_dict(), "epoch": a.epochs}, out / "model_final.pt")
    print(f"=== saved {out / 'model_final.pt'}", flush=True)


@torch.no_grad()
def sample(a, cfg, data, out):
    torch.manual_seed(a.seed)
    np.random.seed(a.seed)
    norm = json.loads((data / "norm.json").read_text())
    heads = np.load(data / "head_train.npy")
    ck = Path(a.ckpt) if a.ckpt else out / "model_final.pt"
    unet = Guide_UNet(cfg).cuda()
    unet.load_state_dict(torch.load(ck, map_location="cuda")["model"])
    unet.eval()
    n_steps = cfg.diffusion.num_diffusion_timesteps
    beta = torch.linspace(cfg.diffusion.beta_start, cfg.diffusion.beta_end, n_steps).cuda()
    skip = n_steps // 100
    seq = list(range(0, n_steps, skip))
    seq_next = [-1] + seq[:-1]
    t0, res = time.time(), []
    for b in range(0, a.n, a.batch):
        m = min(a.batch, a.n - b)
        h = torch.from_numpy(heads[np.random.randint(len(heads), size=m)]).float().cuda()
        x = torch.randn(m, 2, cfg.data.traj_length).cuda()
        for i, j in zip(reversed(seq), reversed(seq_next)):
            t = torch.full((m,), i, device=x.device)
            x = p_xt(x, unet(x, t, h), t, torch.full((m,), j, device=x.device), beta, 0.0)
        res.append(x.transpose(1, 2).cpu().numpy())
    xy = np.concatenate(res) * np.array(norm["std"]) + np.array(norm["mean"])
    path = out / f"samples_s{a.seed}.npy"
    np.save(path, xy.astype(np.float32))
    print(f"=== {len(xy)} trajectories from {ck.name} in {time.time() - t0:.0f} s -> {path}", flush=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["train", "sample"])
    ap.add_argument("--name", default="tdrive_k300")
    ap.add_argument("--exp", required=True)
    ap.add_argument("--epochs", type=int, default=200)
    ap.add_argument("--check", type=int, default=10)
    ap.add_argument("--init", default="", help="train: start from these weights (the authors' model.pt)")
    ap.add_argument("--batch-size", type=int, default=0,
                    help="train: override DiffTraj's batch 1024 (it does not fit an 11 GB GPU)")
    ap.add_argument("--work", default="", help="train: folder for the resume checkpoint (node-local scratch)")
    ap.add_argument("--ckpt", default="", help="sample: checkpoint (default: the newest)")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--n", type=int, default=8761)
    ap.add_argument("--batch", type=int, default=500)
    ap.add_argument("--out-root", default=str(ROOT / "out" / "difftraj"))
    a = ap.parse_args()
    cfg = config()
    data = ROOT / "data_clean" / "difftraj" / a.name
    out = Path(a.out_root) / a.name / a.exp
    out.mkdir(parents=True, exist_ok=True)
    (train if a.mode == "train" else sample)(a, cfg, data, out)


if __name__ == "__main__":
    main()
