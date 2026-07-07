"""Find a seed whose realisation reproduces the published HRs closely.
Runs the generator for many seeds and scores the fit; prints the best."""
import os, subprocess, numpy as np, pandas as pd
from lifelines import CoxPHFitter
from lifelines.statistics import logrank_test

best = None
for seed in range(0, 250):
    env = dict(os.environ, IMB_SEED=str(seed))
    subprocess.run([".venv/bin/python", "generate_imbrave150.py"],
                   env=env, capture_output=True)
    df = pd.read_csv("imbrave150_simulated.csv")
    df["a"] = (df["arm"] == "Atezo+Bev").astype(int)
    hr_os = np.exp(CoxPHFitter().fit(df[["os_time_months","os_event","a"]],
                  "os_time_months","os_event").params_["a"])
    hr_pfs = np.exp(CoxPHFitter().fit(df[["pfs_time_months","pfs_event","a"]],
                   "pfs_time_months","pfs_event").params_["a"])
    A = df["arm"]=="Atezo+Bev"; S=~A
    p = logrank_test(df.loc[A,"os_time_months"], df.loc[S,"os_time_months"],
                     df.loc[A,"os_event"], df.loc[S,"os_event"]).p_value
    score = abs(hr_os-0.58) + abs(hr_pfs-0.59)
    if p < 0.001 and (best is None or score < best[1]):
        best = (seed, score, hr_os, hr_pfs, p)
        print(f"seed={seed}  OS_HR={hr_os:.3f}  PFS_HR={hr_pfs:.3f}  p={p:.1e}  score={score:.3f}")

print("\nBEST:", best)
