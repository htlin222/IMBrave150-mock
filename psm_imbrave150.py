"""
Pool the 10-hospital observational cohort, run propensity-score matching (PSM),
and show that survival analysis on the matched cohort recovers the true effect.

Steps a student performs:
  1. Pool + inspect confounding (naive, biased HR).
  2. Estimate a propensity score (logistic regression, treatment ~ covariates).
  3. 1:1 nearest-neighbour matching with a caliper on the logit(PS).
  4. Check covariate balance (standardised mean differences before/after).
  5. Cox model on the matched cohort  ->  HR ~ 0.58.
"""
import numpy as np
import pandas as pd
from lifelines import CoxPHFitter
from harmonize_hospitals import load_pooled

# Pool the 10 dialect files (this is the "combine 10 hospitals" step),
# then join the hospital catalog to recover site-level attributes.
df = load_pooled("hospitals")
meta = pd.read_csv("hospitals_meta.csv")[["hospital_id", "hospital_region", "hospital_type"]]
df = df.merge(meta, on="hospital_id", how="left")
df["treat"] = (df["arm"] == "Atezo+Bev").astype(int)

# ---- covariates for the propensity model (all measured confounders) ----
COVS = ["age", "ecog_ps", "child_pugh_score", "afp_ge_400",
        "macrovascular_invasion", "extrahepatic_spread", "bclc_C",
        "albi_ge2", "varices_at_baseline", "male", "asia"]
df["bclc_C"]   = (df["bclc_stage"] == "C").astype(int)
df["albi_ge2"] = (df["albi_grade"] >= 2).astype(int)
df["male"]     = (df["sex"] == "Male").astype(int)
df["asia"]     = (df["hospital_region"] == "Asia excluding Japan").astype(int)

def cox_hr(data, tcol, ecol):
    m = CoxPHFitter().fit(data[[tcol, ecol, "treat"]], tcol, ecol)
    hr = np.exp(m.params_["treat"])
    lo, hi = np.exp(m.confidence_intervals_.loc["treat"].values)
    return hr, lo, hi

def smd(data, col):
    a = data.loc[data.treat == 1, col]; b = data.loc[data.treat == 0, col]
    sp = np.sqrt((a.var(ddof=1) + b.var(ddof=1)) / 2)
    return 0.0 if sp == 0 else (a.mean() - b.mean()) / sp

# ---------------------------------------------------------------------------
# 1. Naive (pooled, unadjusted) analysis -- BIASED by confounding
# ---------------------------------------------------------------------------
print("=" * 68)
print("POOLED OBSERVATIONAL COHORT  n =", len(df),
      "| Atezo", int(df.treat.sum()), "/ Sora", int((1-df.treat).sum()))
print("=" * 68)
hr, lo, hi = cox_hr(df, "os_time_months", "os_event")
print(f"[1] NAIVE unadjusted OS HR : {hr:.3f} ({lo:.2f}-{hi:.2f})"
      f"   <- biased (true = 0.58)")

# ---------------------------------------------------------------------------
# 2. Propensity score via logistic regression (Newton-Raphson, no sklearn dep)
# ---------------------------------------------------------------------------
X = np.column_stack([np.ones(len(df))] + [df[c].values.astype(float) for c in COVS])
y = df["treat"].values.astype(float)
beta = np.zeros(X.shape[1])
for _ in range(50):
    p = 1/(1+np.exp(-X@beta)); p = np.clip(p, 1e-6, 1-1e-6)
    W = p*(1-p)
    grad = X.T@(y-p)
    H = (X*W[:,None]).T@X + 1e-8*np.eye(X.shape[1])
    beta += np.linalg.solve(H, grad)
ps = 1/(1+np.exp(-X@beta))
df["ps"] = ps
df["logit_ps"] = np.log(ps/(1-ps))

# ---------------------------------------------------------------------------
# 3. 1:1 nearest-neighbour matching on logit(PS), caliper = 0.2 * SD
# ---------------------------------------------------------------------------
caliper = 0.2 * df["logit_ps"].std()
treated = df[df.treat == 1].sort_values("logit_ps").copy()
control = df[df.treat == 0].copy()
ctrl_idx = control.index.to_numpy()
ctrl_lp  = control["logit_ps"].to_numpy()
used = np.zeros(len(control), dtype=bool)
pairs = []
for ti, tlp in zip(treated.index, treated["logit_ps"]):
    d = np.abs(ctrl_lp - tlp)
    d[used] = np.inf
    j = int(np.argmin(d))
    if d[j] <= caliper:
        used[j] = True
        pairs.append((ti, ctrl_idx[j]))
matched_idx = [i for pair in pairs for i in pair]
m = df.loc[matched_idx].copy()
print(f"\n[2] Propensity model fitted on {len(COVS)} covariates.")
print(f"[3] 1:1 caliper matching -> {len(pairs)} matched pairs "
      f"({len(m)} patients, caliper={caliper:.3f} on logit PS)")

# ---------------------------------------------------------------------------
# 4. Balance check: standardised mean differences (|SMD|<0.1 = balanced)
# ---------------------------------------------------------------------------
print("\n[4] Covariate balance (|SMD|, rule of thumb: <0.10 good)")
print(f"    {'covariate':<24}{'before':>9}{'after':>9}")
for c in COVS:
    print(f"    {c:<24}{abs(smd(df,c)):>9.3f}{abs(smd(m,c)):>9.3f}")

# ---------------------------------------------------------------------------
# 5. Survival analysis on matched cohort -> recovers HR ~ 0.58
# ---------------------------------------------------------------------------
print("\n[5] SURVIVAL ANALYSIS")
hr, lo, hi = cox_hr(m, "os_time_months", "os_event")
print(f"    OS  HR (matched)  : {hr:.3f} ({lo:.2f}-{hi:.2f})   [truth 0.58, trial 0.58]")
hr, lo, hi = cox_hr(m, "pfs_time_months", "pfs_event")
print(f"    PFS HR (matched)  : {hr:.3f} ({lo:.2f}-{hi:.2f})   [truth 0.59, trial 0.59]")

# For comparison: multivariable regression adjustment on the full cohort
mv = df[["os_time_months","os_event","treat"]+COVS].copy()
hr_adj = np.exp(CoxPHFitter().fit(mv,"os_time_months","os_event").params_["treat"])
print(f"    OS  HR (full-cohort regression adjustment) : {hr_adj:.3f}"
      f"   (should also ~0.58)")
print("=" * 68)
