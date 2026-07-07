"""
TMLE on the 10-hospital cohort -- and why the estimand matters.

PSM / IPTW / Cox all reported a conditional HAZARD RATIO. TMLE instead targets
a MARGINAL causal estimand; here we take the difference in the probability of
death BY 12 MONTHS between the two treatments (a risk difference on the survival
scale -- the same scale as the trial's "12-month OS 67% vs 55%").

Because this is simulated data we KNOW the data-generating mechanism, so we can
compute the TRUE marginal risk difference analytically and check that TMLE hits
it while the naive contrast is biased by confounding.

Estimators compared (all for RD = P(dead by 12 | treat) - P(dead by 12 | control)):
  * NAIVE   : raw complete-case difference (biased)
  * G-comp  : outcome regression only (single robustness)
  * IPTW    : propensity weighting only (single robustness)
  * AIPW    : augmented IPW / one-step -- DOUBLY ROBUST
  * TMLE    : targeted MLE with IPCW for censoring -- DOUBLY ROBUST + efficient

Right-censoring before 12 months is handled by IPCW (a censoring model).
Deterministic: no randomness; reproduces exactly.
"""
import numpy as np
import pandas as pd
from harmonize_hospitals import load_pooled

LANDMARK = 12.0

# ---------------------------------------------------------------------------
# Pooled cohort + measured confounders W
# ---------------------------------------------------------------------------
df = load_pooled("hospitals")
df["treat"]    = (df["arm"] == "Atezo+Bev").astype(int)
df["bclc_C"]   = (df["bclc_stage"] == "C").astype(int)
df["albi_ge2"] = (df["albi_grade"] >= 2).astype(int)
df["male"]     = (df["sex"] == "Male").astype(int)
# hospital (site) drives BOTH prescribing preference and prognosis -> a
# site-level confounder. Include site dummies (drop H01) or residual
# confounding remains.
hdum = pd.get_dummies(df["hospital_id"], prefix="site", drop_first=True).astype(float)
df = pd.concat([df, hdum], axis=1)
W = ["age", "ecog_ps", "child_pugh_score", "afp_ge_400", "macrovascular_invasion",
     "extrahepatic_spread", "bclc_C", "albi_ge2", "varices_at_baseline", "male"] \
    + list(hdum.columns)

A = df["treat"].values.astype(float)

# ---------------------------------------------------------------------------
# TRUE marginal estimand from the known DGP (analytic)
#   rate_a(X) = exp(ln 0.05 + ln0.58*a + lp_c(X) + hospital_frailty)
#   S_a(12) = exp(-12*rate_a);  R_a = 1 - S_a
# ---------------------------------------------------------------------------
lp = (np.log(1.55)*df["afp_ge_400"] + np.log(1.45)*df["macrovascular_invasion"] +
      np.log(1.30)*df["extrahepatic_spread"] + np.log(1.35)*df["ecog_ps"] +
      np.log(1.25)*df["bclc_C"] + np.log(1.20)*df["albi_ge2"]).values
lp_c = lp - lp.mean()
FRAILTY = dict(zip([f"H{i:02d}" for i in range(1, 11)],
                   [-0.10, 0.05, -0.06, 0.12, 0.02, -0.04, 0.15, -0.08, 0.06, 0.03]))
hfr = df["hospital_id"].map(FRAILTY).values
rate1 = np.exp(np.log(0.05) + np.log(0.58)*1 + lp_c + hfr)
rate0 = np.exp(np.log(0.05) + np.log(0.58)*0 + lp_c + hfr)
R1_true = (1 - np.exp(-LANDMARK*rate1)).mean()
R0_true = (1 - np.exp(-LANDMARK*rate0)).mean()
RD_true = R1_true - R0_true          # true causal risk difference (death by 12m)

# ---------------------------------------------------------------------------
# Landmark outcome Y = I(dead by 12) with censoring indicator Delta
#   Delta = 1 if the 12-month status is known:
#     died by 12 (event & time<=12)  -> Y=1
#     alive at 12 (time>=12)         -> Y=0
#   Delta = 0 if censored before 12 (no event & time<12) -> Y unknown
# ---------------------------------------------------------------------------
t, e = df["os_time_months"].values, df["os_event"].values
Y = np.where((e == 1) & (t <= LANDMARK), 1.0,
     np.where(t >= LANDMARK, 0.0, np.nan))
Delta = (~np.isnan(Y)).astype(float)
Yc = np.nan_to_num(Y, nan=0.0)       # placeholder for censored

# ---------------------------------------------------------------------------
# logistic regression helper (Newton-Raphson, ridge-stabilised)
# ---------------------------------------------------------------------------
def logit_fit(Xc, y, w=None):
    if w is None:
        w = np.ones(len(y))
    b = np.zeros(Xc.shape[1])
    for _ in range(100):
        p = np.clip(1/(1+np.exp(-Xc@b)), 1e-9, 1-1e-9)
        Wd = w*p*(1-p)
        g = Xc.T@(w*(y-p))
        H = (Xc*Wd[:, None]).T@Xc + 1e-6*np.eye(Xc.shape[1])
        step = np.linalg.solve(H, g)
        b += step
        if np.max(np.abs(step)) < 1e-8:
            break
    return b

def design(cols, treat=None):
    mats = [np.ones(len(df))]
    if treat is not None:
        mats.append(treat)
    mats += [df[c].astype(float).values for c in cols]
    return np.column_stack(mats)

expit = lambda z: 1/(1+np.exp(-z))

# ---- treatment mechanism g(W)=P(A=1|W) ----
Xg = design(W)
gW = np.clip(expit(Xg@logit_fit(Xg, A)), 0.02, 0.98)

# ---- censoring weights via Kaplan-Meier of the censoring distribution ----
# Censoring here is administrative (independent of X), so the correct IPCW
# denominator is G(u)=P(C>u), estimated by KM treating censorings as events.
# gc_i = G(min(t_i, 12)):  died-by-12 -> G(t_i);  alive-at-12 -> G(12).
from lifelines import KaplanMeierFitter
kmG = KaplanMeierFitter().fit(df["os_time_months"], 1 - df["os_event"])
u = np.minimum(df["os_time_months"].values, LANDMARK)
gc = np.clip(kmG.survival_function_at_times(u).values, 0.05, 1.0)

# ---- outcome model Q(A,W)=P(Y=1|A,W,Delta=1) ----
obs = Delta == 1
Xq_full = design(W, treat=A)
bq = logit_fit(Xq_full[obs], Yc[obs])
def Qbar(a):
    Xq = design(W, treat=np.full(len(df), float(a)))
    return np.clip(expit(Xq@bq), 1e-6, 1-1e-6)
Q1, Q0 = Qbar(1), Qbar(0)
QA = np.where(A == 1, Q1, Q0)

# ===========================================================================
# Estimators
# ===========================================================================
def naive():
    m = obs
    return Yc[m & (A == 1)].mean() - Yc[m & (A == 0)].mean()

def gcomp():
    return Q1.mean() - Q0.mean()

def iptw():
    m = obs
    w1 = (A*Delta)/(gW*gc)
    w0 = ((1-A)*Delta)/((1-gW)*gc)
    R1 = np.sum(w1*Yc)/np.sum(w1)
    R0 = np.sum(w0*Yc)/np.sum(w0)
    return R1 - R0

def aipw():
    # augmented IPW (one-step, doubly robust)
    dr1 = (A*Delta)/(gW*gc)*(Yc - Q1) + Q1
    dr0 = ((1-A)*Delta)/((1-gW)*gc)*(Yc - Q0) + Q0
    est = dr1.mean() - dr0.mean()
    ic = dr1 - dr0 - est
    return est, ic.std(ddof=1)/np.sqrt(len(df))

def tmle():
    # clever covariates (with IPCW), fluctuate the outcome model
    H1 = Delta/(gW*gc)            # for a=1
    H0 = -Delta/((1-gW)*gc)       # for a=0
    Hobs = np.where(A == 1, H1, H0)
    # fluctuation: logistic of Y on Hobs, offset logit(QA), fit on observed
    off = np.log(QA/(1-QA))
    m = obs
    # 1-D Newton for epsilon
    eps = 0.0
    for _ in range(200):
        p = expit(off[m] + eps*Hobs[m])
        grad = np.sum(Hobs[m]*(Yc[m]-p))
        hess = -np.sum(Hobs[m]**2*p*(1-p)) - 1e-8
        step = grad/hess
        eps -= step
        if abs(step) < 1e-10:
            break
    Q1s = expit(np.log(Q1/(1-Q1)) + eps*(1/(gW*gc)))
    Q0s = expit(np.log(Q0/(1-Q0)) + eps*(-1/((1-gW)*gc)))
    est = Q1s.mean() - Q0s.mean()
    # influence curve for SE
    ic = (Delta*A/(gW*gc))*(Yc-Q1s) - (Delta*(1-A)/((1-gW)*gc))*(Yc-Q0s) \
         + (Q1s-Q0s) - est
    return est, ic.std(ddof=1)/np.sqrt(len(df))

aipw_est, aipw_se = aipw()
tmle_est, tmle_se = tmle()

print("="*64)
print(f"Estimand: risk difference in DEATH BY {LANDMARK:.0f} MONTHS  (treat - control)")
print(f"          negative = fewer deaths with atezo+bev")
print("="*64)
print(f"  TRUE  (from DGP)     : {RD_true:+.3f}   "
      f"[= {R1_true:.3f} - {R0_true:.3f};  survival gap {(-RD_true)*100:.1f} pts]")
print(f"  NAIVE complete-case  : {naive():+.3f}   <- biased (confounded)")
print(f"  G-computation        : {gcomp():+.3f}")
print(f"  IPTW                 : {iptw():+.3f}")
print(f"  AIPW  (doubly robust): {aipw_est:+.3f}  (SE {aipw_se:.3f})")
print(f"  TMLE  (doubly robust): {tmle_est:+.3f}  (SE {tmle_se:.3f})  "
      f"95% CI [{tmle_est-1.96*tmle_se:+.3f}, {tmle_est+1.96*tmle_se:+.3f}]")
print("="*64)
print("Note: TMLE targets a MARGINAL risk difference, not the Cox hazard ratio.")
print("Estimand first, method second -- they live on different scales.")
