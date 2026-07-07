"""
Specification-curve / "multiverse" robustness demo.

Fixes the DATA (seed 48) and sweeps ~120 defensible ANALYTIC choices:
    method      : PSM matching  |  IPTW weighting  |  regression adjustment
    covariates  : full set, each leave-one-out, and a few minimal sets
    caliper     : 0.1 / 0.2 / 0.5   (matching only)
    ratio       : 1:1 / 1:2         (matching only)

Point of the picture: the NAIVE (unadjusted) estimate sits alone and biased
(~0.51), while every reasonable confounding-adjustment lands in a tight band
around the true / trial value 0.58. The number is not deterministic across
analytic choices -- the STORY is.

Deterministic: no randomness anywhere, so this script reproduces exactly.
Writes robustness_multiverse.png and prints a summary.
"""
import itertools
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from lifelines import CoxPHFitter
from harmonize_hospitals import load_pooled

# ---- pooled cohort + derived covariates -----------------------------------
df = load_pooled("hospitals")
meta = pd.read_csv("hospitals_meta.csv")[["hospital_id", "hospital_region"]]
df = df.merge(meta, on="hospital_id", how="left")
df["treat"]    = (df["arm"] == "Atezo+Bev").astype(int)
df["bclc_C"]   = (df["bclc_stage"] == "C").astype(int)
df["albi_ge2"] = (df["albi_grade"] >= 2).astype(int)
df["male"]     = (df["sex"] == "Male").astype(int)
df["asia"]     = (df["hospital_region"] == "Asia excluding Japan").astype(int)

FULL = ["age", "ecog_ps", "child_pugh_score", "afp_ge_400", "macrovascular_invasion",
        "extrahepatic_spread", "bclc_C", "albi_ge2", "varices_at_baseline", "male", "asia"]

# covariate sets: full, every leave-one-out, plus 3 curated minimal sets
COVSETS = {"full": FULL}
for c in FULL:
    COVSETS[f"drop_{c}"] = [x for x in FULL if x != c]
COVSETS["core4"]   = ["afp_ge_400", "macrovascular_invasion", "ecog_ps", "albi_ge2"]
COVSETS["core6"]   = ["afp_ge_400", "macrovascular_invasion", "extrahepatic_spread",
                      "ecog_ps", "albi_ge2", "varices_at_baseline"]
COVSETS["clin+site"] = ["afp_ge_400", "macrovascular_invasion", "ecog_ps", "asia"]

def propensity(covs):
    X = np.column_stack([np.ones(len(df))] + [df[c].astype(float).values for c in covs])
    y = df["treat"].values.astype(float)
    beta = np.zeros(X.shape[1])
    for _ in range(60):
        p = np.clip(1/(1+np.exp(-X@beta)), 1e-6, 1-1e-6)
        W = p*(1-p)
        beta += np.linalg.solve((X*W[:, None]).T@X + 1e-8*np.eye(X.shape[1]), X.T@(y-p))
    return np.clip(1/(1+np.exp(-X@beta)), 1e-6, 1-1e-6)

def cox_hr(data, weights=None):
    cols = ["os_time_months", "os_event", "treat"]
    d = data[cols].copy()
    if weights is not None:
        d["w"] = weights
        m = CoxPHFitter().fit(d, "os_time_months", "os_event",
                              weights_col="w", robust=True)
    else:
        m = CoxPHFitter().fit(d, "os_time_months", "os_event")
    hr = np.exp(m.params_["treat"])
    lo, hi = np.exp(m.confidence_intervals_.loc["treat"].values)
    return hr, lo, hi

def match(ps, k, caliper_sd):
    lp = np.log(ps/(1-ps))
    df2 = df.assign(lp=lp)
    cal = caliper_sd * df2["lp"].std()
    tr = df2[df2.treat == 1].sort_values("lp")
    ct = df2[df2.treat == 0]
    c_idx, c_lp = ct.index.to_numpy(), ct["lp"].to_numpy()
    used = np.zeros(len(ct), dtype=bool)
    keep = []
    for ti, tlp in zip(tr.index, tr["lp"]):
        d = np.abs(c_lp - tlp); d[used] = np.inf
        order = np.argsort(d)[:k]
        got = [j for j in order if d[j] <= cal]
        if got:
            keep.append(ti)
            for j in got:
                used[j] = True; keep.append(c_idx[j])
    return df.loc[keep]

# ---- naive baseline --------------------------------------------------------
naive_hr, naive_lo, naive_hi = cox_hr(df)

# ---- sweep -----------------------------------------------------------------
rows = []
for name, covs in COVSETS.items():
    ps = propensity(covs)
    # regression adjustment
    d = df[["os_time_months", "os_event", "treat"] + covs]
    m = CoxPHFitter().fit(d, "os_time_months", "os_event")
    hr = np.exp(m.params_["treat"]); lo, hi = np.exp(m.confidence_intervals_.loc["treat"].values)
    rows.append(dict(method="Regression", covset=name, hr=hr, lo=lo, hi=hi))
    # IPTW (stabilized ATE weights)
    p_treat = df["treat"].mean()
    w = np.where(df.treat == 1, p_treat/ps, (1-p_treat)/(1-ps))
    hr, lo, hi = cox_hr(df, weights=w)
    rows.append(dict(method="IPTW", covset=name, hr=hr, lo=lo, hi=hi))
    # PSM matching over caliper x ratio
    for cal, k in itertools.product([0.1, 0.2, 0.5], [1, 2]):
        mm = match(ps, k, cal)
        hr, lo, hi = cox_hr(mm)
        rows.append(dict(method="PSM matching", covset=name,
                         caliper=cal, ratio=k, hr=hr, lo=lo, hi=hi, n=len(mm)))

res = pd.DataFrame(rows)
res.to_csv("robustness_multiverse_results.csv", index=False)

# ---- summary ---------------------------------------------------------------
adj = res["hr"].values
print(f"Naive (unadjusted) OS HR : {naive_hr:.3f} ({naive_lo:.2f}-{naive_hi:.2f})")
print(f"Adjusted specifications  : {len(adj)}")
print(f"  median HR              : {np.median(adj):.3f}")
print(f"  IQR                    : {np.percentile(adj,25):.3f} - {np.percentile(adj,75):.3f}")
print(f"  range                  : {adj.min():.3f} - {adj.max():.3f}")
print(f"  within 0.55-0.61       : {100*np.mean((adj>=0.55)&(adj<=0.61)):.0f}%")

# ---------------------------------------------------------------------------
# Figure: specification curve (left) + HR histogram (right)
# Palette: Okabe-Ito (colorblind-safe)
# ---------------------------------------------------------------------------
OK = {"PSM matching": "#0072B2", "IPTW": "#E69F00", "Regression": "#009E73"}
NAIVE_C, TRUTH_C, INK, MUTED = "#D55E00", "#555555", "#222222", "#888888"
plt.rcParams.update({"font.size": 11, "axes.edgecolor": "#cccccc",
                     "axes.linewidth": 0.8, "figure.dpi": 130})

fig, (axL, axR) = plt.subplots(1, 2, figsize=(12.5, 6.2),
                               gridspec_kw={"width_ratios": [2.4, 1]})

# --- left: specification curve, sorted by HR ---
s = res.sort_values("hr").reset_index(drop=True)
x = np.arange(len(s))
for meth, c in OK.items():
    mask = s["method"] == meth
    axL.errorbar(x[mask], s.loc[mask, "hr"],
                 yerr=[s.loc[mask, "hr"]-s.loc[mask, "lo"], s.loc[mask, "hi"]-s.loc[mask, "hr"]],
                 fmt="o", ms=5, color=c, ecolor=c, elinewidth=1, capsize=0,
                 alpha=0.9, label=meth, zorder=3)
axL.axhline(0.58, color=TRUTH_C, ls="--", lw=1.6, zorder=2)
axL.axhline(naive_hr, color=NAIVE_C, ls=":", lw=1.8, zorder=2)
axL.text(len(s)*0.015, 0.585, "truth / trial  HR 0.58", va="bottom", ha="left",
         color=TRUTH_C, fontsize=10, fontweight="bold")
axL.text(len(s)*0.015, 0.497, f"naïve (confounded)  HR {naive_hr:.2f}", va="top",
         ha="left", color=NAIVE_C, fontsize=10, fontweight="bold")
axL.set_xlabel("analytic specification  (sorted by estimated HR)", color=INK)
axL.set_ylabel("Overall-survival hazard ratio (Atezo+Bev vs Sorafenib)", color=INK)
axL.set_title(f"Every reasonable adjustment lands near 0.58  ·  {len(s)} specifications",
              loc="left", fontsize=12, fontweight="bold", color=INK)
axL.legend(frameon=False, loc="lower right", title="adjustment method")
axL.spines[["top", "right"]].set_visible(False)
axL.grid(axis="y", color="#eeeeee", lw=0.8)
axL.set_ylim(min(0.42, naive_lo-0.02), 0.82)

# --- right: histogram of adjusted HRs, naive marked ---
axR.hist(adj, bins=18, color="#8fbfe0", edgecolor="white", linewidth=0.6)
axR.axvline(0.58, color=TRUTH_C, ls="--", lw=1.6)
axR.axvline(naive_hr, color=NAIVE_C, ls=":", lw=1.8)
axR.axvline(np.median(adj), color=INK, lw=1.4)
axR.text(np.median(adj), axR.get_ylim()[1]*0.98, f" median {np.median(adj):.2f}",
         va="top", ha="left", color=INK, fontsize=9)
axR.text(naive_hr, axR.get_ylim()[1]*0.60, f"naïve\n{naive_hr:.2f} ",
         va="center", ha="right", color=NAIVE_C, fontsize=9, fontweight="bold")
axR.set_xlabel("adjusted HR", color=INK)
axR.set_ylabel("number of specifications", color=INK)
axR.set_title("distribution of adjusted HRs", loc="left", fontsize=11, color=INK)
axR.spines[["top", "right"]].set_visible(False)
axR.grid(axis="y", color="#eeeeee", lw=0.8)

fig.suptitle("Robustness of the treatment effect across analytic choices "
             "(data fixed, methods varied)", x=0.01, ha="left",
             fontsize=13.5, fontweight="bold", color=INK)
fig.tight_layout(rect=[0, 0, 1, 0.96])
fig.savefig("robustness_multiverse.png", bbox_inches="tight")
print("\nWrote robustness_multiverse.png and robustness_multiverse_results.csv")
