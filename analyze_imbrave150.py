"""
Reproduce the key IMbrave150 results from the simulated dataset using the
same statistical methods as the paper: Kaplan-Meier, log-rank, Cox PH.
Prints a side-by-side comparison against the published numbers.
"""
import numpy as np
import pandas as pd
from lifelines import KaplanMeierFitter, CoxPHFitter
from lifelines.statistics import logrank_test

df = pd.read_csv("imbrave150_simulated.csv")
df["arm_atezo"] = (df["arm"] == "Atezo+Bev").astype(int)

def km_rate(mask, t_col, e_col, t):
    kmf = KaplanMeierFitter().fit(df.loc[mask, t_col], df.loc[mask, e_col])
    return float(kmf.predict(t))

def median(mask, t_col, e_col):
    kmf = KaplanMeierFitter().fit(df.loc[mask, t_col], df.loc[mask, e_col])
    return kmf.median_survival_time_

A = df["arm"] == "Atezo+Bev"
S = df["arm"] == "Sorafenib"

print("=" * 70)
print("IMbrave150 simulated data — reproduction check")
print("=" * 70)

# ---- Overall survival ----
cph_os = CoxPHFitter().fit(df[["os_time_months", "os_event", "arm_atezo"]],
                           "os_time_months", "os_event")
hr_os = np.exp(cph_os.params_["arm_atezo"])
ci_os = np.exp(cph_os.confidence_intervals_.loc["arm_atezo"].values)
lr_os = logrank_test(df.loc[A, "os_time_months"], df.loc[S, "os_time_months"],
                     df.loc[A, "os_event"], df.loc[S, "os_event"])

print("\n--- OVERALL SURVIVAL ---")
print(f"  Deaths: Atezo+Bev {df.loc[A,'os_event'].sum()}/{A.sum()} "
      f"({df.loc[A,'os_event'].mean()*100:.1f}%) | "
      f"Sorafenib {df.loc[S,'os_event'].sum()}/{S.sum()} "
      f"({df.loc[S,'os_event'].mean()*100:.1f}%)")
print(f"  Cox HR (death)         : {hr_os:.3f}  95% CI {ci_os[0]:.2f}-{ci_os[1]:.2f}"
      f"   [paper 0.58, 0.42-0.79]")
print(f"  Log-rank p             : {lr_os.p_value:.2e}          [paper <0.001]")
print(f"  12-mo OS Atezo+Bev     : {km_rate(A,'os_time_months','os_event',12)*100:.1f}%"
      f"        [paper 67.2%]")
print(f"  12-mo OS Sorafenib     : {km_rate(S,'os_time_months','os_event',12)*100:.1f}%"
      f"        [paper 54.6%]")

# ---- Progression-free survival ----
cph_pfs = CoxPHFitter().fit(df[["pfs_time_months", "pfs_event", "arm_atezo"]],
                            "pfs_time_months", "pfs_event")
hr_pfs = np.exp(cph_pfs.params_["arm_atezo"])
ci_pfs = np.exp(cph_pfs.confidence_intervals_.loc["arm_atezo"].values)

print("\n--- PROGRESSION-FREE SURVIVAL ---")
print(f"  Cox HR (progression)   : {hr_pfs:.3f}  95% CI {ci_pfs[0]:.2f}-{ci_pfs[1]:.2f}"
      f"   [paper 0.59, 0.47-0.76]")
print(f"  Median PFS Atezo+Bev   : {median(A,'pfs_time_months','pfs_event'):.1f} mo"
      f"          [paper 6.8]")
print(f"  Median PFS Sorafenib   : {median(S,'pfs_time_months','pfs_event'):.1f} mo"
      f"          [paper 4.3]")

# ---- Response ----
orr_a = df.loc[A, "objective_response"].mean() * 100
orr_s = df.loc[S, "objective_response"].mean() * 100
print("\n--- OBJECTIVE RESPONSE (RECIST 1.1) ---")
print(f"  ORR Atezo+Bev          : {orr_a:.1f}%           [paper 27.3%]")
print(f"  ORR Sorafenib          : {orr_s:.1f}%           [paper 11.9%]")

# ---- Safety ----
print("\n--- SAFETY ---")
print(f"  Grade 3/4 AE Atezo+Bev : {df.loc[A,'grade34_adverse_event'].mean()*100:.1f}%"
      f"        [paper 56.5%]")
print(f"  Grade 3/4 AE Sorafenib : {df.loc[S,'grade34_adverse_event'].mean()*100:.1f}%"
      f"        [paper 55.1%]")
print(f"  Gr3/4 HTN Atezo+Bev    : {df.loc[A,'grade34_hypertension'].mean()*100:.1f}%"
      f"        [paper 15.2%]")

# ---- Multivariable Cox (teaching extension) ----
print("\n--- MULTIVARIABLE COX (OS, adjusted) ---")
mv = df[["os_time_months", "os_event", "arm_atezo", "afp_ge_400",
         "macrovascular_invasion", "extrahepatic_spread", "ecog_ps"]].copy()
cph_mv = CoxPHFitter().fit(mv, "os_time_months", "os_event")
print(cph_mv.summary[["coef", "exp(coef)", "p"]].round(3).to_string())
print("=" * 70)
