"""
META-LAYER (v2): synthesize TEN SEPARATE hospital files that must be pooled.

Each hospital exports its own CSV, and -- like the real world -- the files do
NOT share a schema. They come from three different "EHR vendors" with different
column names, value codings, units and missing-value conventions:

    Vendor Alpha (H01,H04,H07,H10) : the canonical / tidy layout
    Vendor Beta  (H02,H05,H08)     : European units (g/L, umol/L), M/F, "NA"
    Vendor Gamma (H03,H06,H09)     : registry style, 1/0 codes, only AFP>=400,
                                     Child-Pugh as "A5"/"A6", no continuous AFP

The demo / student task:
    1. discover + read all 10 files (hospitals/*.csv)
    2. HARMONISE them to one schema (rename, recode, unit-convert)
    3. pool -> one observational cohort (confounded by indication)
    4. propensity-score matching -> survival analysis -> recover HR ~0.58

The underlying patient data is generated EXACTLY as validated (seed 48), then
split into the 10 dialect files, so the pooled analysis still gives the tuned
result (naive OS HR ~0.51, PSM/adjusted ~0.58). An answer-key pooled file is
also written for validation (_answer_key_pooled.csv) -- do not hand this to
students; it is what a correct harmonisation must reproduce.
"""
import os
import numpy as np
import pandas as pd

SEED = int(os.environ.get("IMB_MH_SEED", "48"))
RNG = np.random.default_rng(SEED)

def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))

# ---------------------------------------------------------------------------
# 1. Ten hospitals (unequal size, type, region, prescribing culture, vendor)
# ---------------------------------------------------------------------------
hosp = pd.DataFrame({
    "hospital_id":  [f"H{i:02d}" for i in range(1, 11)],
    "hospital_name": ["Northshore University","Riverside General","Metropolitan Cancer Ctr",
                       "St Aldys Community","Lakeside Regional","Harbor City Medical",
                       "Pinecrest Community","Eastgate University","Valley District",
                       "Summit General"],
    "hospital_type": ["Academic","Community","Academic","Community","Regional","Academic",
                      "Community","Academic","Community","Regional"],
    "hospital_region": ["Asia excluding Japan","Rest of World","Asia excluding Japan",
                        "Rest of World","Asia excluding Japan","Rest of World",
                        "Asia excluding Japan","Rest of World","Asia excluding Japan",
                        "Rest of World"],
    "ehr_vendor": ["Alpha","Beta","Gamma","Alpha","Beta","Alpha","Alpha","Beta","Gamma","Alpha"],
    "n_patients": [320, 285, 240, 95, 180, 210, 75, 155, 110, 130],  # unequal, sum=1800
    "atezo_pref_logit": [ 0.85, -0.35, 0.70, -0.55, 0.10, 0.55, -0.70, 0.60, -0.25, -0.10],
    "hbv_frac": [0.62, 0.30, 0.60, 0.28, 0.55, 0.33, 0.58, 0.31, 0.57, 0.35],
    "frailty":  [-0.10, 0.05, -0.06, 0.12, 0.02, -0.04, 0.15, -0.08, 0.06, 0.03],
})
# Vendor Gamma actually lives at H03,H06,H09 per the docstring; fix mapping:
hosp["ehr_vendor"] = ["Alpha","Beta","Gamma","Alpha","Beta","Gamma","Alpha","Beta","Gamma","Alpha"]

hid   = np.repeat(hosp["hospital_id"].values,   hosp["n_patients"].values)
hpref = np.repeat(hosp["atezo_pref_logit"].values, hosp["n_patients"].values)
hhbv  = np.repeat(hosp["hbv_frac"].values,      hosp["n_patients"].values)
hfr   = np.repeat(hosp["frailty"].values,       hosp["n_patients"].values)
N = len(hid)

# ---------------------------------------------------------------------------
# 2. Baseline covariates (unchanged generative process -> validated stats)
# ---------------------------------------------------------------------------
age = np.clip(np.round(RNG.normal(64, 11.5, N)), 18, 90).astype(int)
sex = np.where(RNG.random(N) < 0.82, "Male", "Female")
u = RNG.random(N)
etiology = np.where(u < hhbv, "HBV", np.where(u < hhbv + 0.22, "HCV", "Nonviral"))
ecog_ps = (RNG.random(N) < 0.40).astype(int)
child_pugh_score = np.where(RNG.random(N) < 0.70, 5, 6)
afp_ge_400 = (RNG.random(N) < 0.38).astype(int)
macrovascular_invasion = (RNG.random(N) < 0.38).astype(int)
extrahepatic_spread = (RNG.random(N) < 0.62).astype(int)
mvi_or_ehs = ((macrovascular_invasion + extrahepatic_spread) > 0).astype(int)
bclc_C = (RNG.random(N) < 0.82).astype(int)
bclc_stage = np.where(bclc_C == 1, "C", np.where(RNG.random(N) < 0.8, "B", "A"))
varices_at_baseline = (RNG.random(N) < 0.28).astype(int)
albumin = np.round(np.clip(RNG.normal(3.9, 0.45, N), 2.4, 5.2), 1)
bilirubin = np.round(np.clip(RNG.lognormal(np.log(0.8), 0.45, N), 0.2, 4.0), 2)
albi_score = 0.66*np.log10(bilirubin*17.1) - 0.085*(albumin*10.0)
albi_grade = np.where(albi_score <= -2.60, 1, np.where(albi_score <= -1.39, 2, 3))
afp = np.where(afp_ge_400 == 1, RNG.lognormal(np.log(2500), 1.3, N),
               RNG.lognormal(np.log(40), 1.6, N))
afp = np.clip(np.round(afp, 1), 1.0, 600000.0)

# ---------------------------------------------------------------------------
# 3. Confounded treatment assignment + outcomes (TRUE HR 0.58/0.59)
# ---------------------------------------------------------------------------
lp = (np.log(1.55)*afp_ge_400 + np.log(1.45)*macrovascular_invasion +
      np.log(1.30)*extrahepatic_spread + np.log(1.35)*ecog_ps +
      np.log(1.25)*bclc_C + np.log(1.20)*(albi_grade >= 2).astype(int))
lp_c = lp - lp.mean()
GAMMA = 1.25
logit_atezo = hpref - GAMMA*lp_c - 0.55*varices_at_baseline - 0.015*(age-64)
is_atezo = (RNG.random(N) < sigmoid(logit_atezo)).astype(int)
arm = np.where(is_atezo == 1, "Atezo+Bev", "Sorafenib")

loghaz_common = lp_c + hfr
rate_os = np.exp(np.log(0.050) + np.log(0.58)*is_atezo + loghaz_common)
true_os = RNG.exponential(1.0/rate_os)
k_pfs, med_s = 1.15, 5.9
scale_s = med_s/(np.log(2)**(1.0/k_pfs))
mult_pfs = np.exp(np.log(0.59)*is_atezo + loghaz_common)
true_pfs = np.minimum(scale_s*(RNG.exponential(1.0, N)/mult_pfs)**(1.0/k_pfs), true_os)

entry = RNG.uniform(0.0, 24.0, N)
enroll_year = np.where(entry < 12, 2018, 2019)
enroll_month = RNG.integers(1, 13, N)
cens = np.minimum(24.0 - entry, RNG.exponential(60.0, N))
os_time = np.round(np.minimum(true_os, cens), 2)
os_event = (true_os <= cens).astype(int)
pfs_time = np.round(np.minimum(true_pfs, cens), 2)
pfs_event = (true_pfs <= cens).astype(int)

objective_response = (RNG.random(N) < np.where(is_atezo == 1, 0.27, 0.12)).astype(int)
best = np.where(objective_response == 1, np.where(RNG.random(N) < 0.2, "CR", "PR"),
                np.where(RNG.random(N) < 0.55, "SD", np.where(RNG.random(N) < 0.78, "PD", "NE")))
grade34_ae = (RNG.random(N) < np.where(is_atezo == 1, 0.565, 0.551)).astype(int)
grade34_htn = (RNG.random(N) < np.where(is_atezo == 1, 0.152, 0.121)).astype(int)

def punch(x, frac):
    x = x.astype(float).copy(); x[RNG.random(N) < frac] = np.nan; return x
afp_rec = punch(afp, 0.06)
albumin_rec = punch(albumin, 0.05)
bilirubin_rec = punch(bilirubin, 0.05)

# canonical (answer-key) pooled frame
canon = pd.DataFrame({
    "patient_id": [f"RW-{i:05d}" for i in range(1, N+1)],
    "hospital_id": hid, "enroll_year": enroll_year, "enroll_month": enroll_month,
    "arm": arm, "age": age, "sex": sex, "etiology": etiology, "ecog_ps": ecog_ps,
    "child_pugh_score": child_pugh_score, "albi_grade": albi_grade,
    "albumin_g_dl": albumin_rec, "bilirubin_mg_dl": bilirubin_rec,
    "bclc_stage": bclc_stage, "afp_ng_ml": afp_rec, "afp_ge_400": afp_ge_400,
    "macrovascular_invasion": macrovascular_invasion,
    "extrahepatic_spread": extrahepatic_spread, "mvi_or_ehs": mvi_or_ehs,
    "varices_at_baseline": varices_at_baseline,
    "os_time_months": os_time, "os_event": os_event,
    "pfs_time_months": pfs_time, "pfs_event": pfs_event,
    "best_overall_response": best, "objective_response": objective_response,
    "grade34_adverse_event": grade34_ae, "grade34_hypertension": grade34_htn,
})
canon.to_csv("_answer_key_pooled.csv", index=False)
hosp.drop(columns=["atezo_pref_logit","hbv_frac","frailty"]).to_csv("hospitals_meta.csv", index=False)

# ---------------------------------------------------------------------------
# 4. Split into 10 per-hospital files, each in its vendor "dialect"
# ---------------------------------------------------------------------------
os.makedirs("hospitals", exist_ok=True)

def yn(v):   # 1/0 -> Yes/No, NaN-safe
    return pd.Series(v).map({1: "Yes", 0: "No", 1.0: "Yes", 0.0: "No"})

def emit_alpha(g, path):   # canonical tidy layout, blank missing
    out = g[["patient_id","hospital_id","arm","age","sex","etiology","ecog_ps",
             "child_pugh_score","albi_grade","albumin_g_dl","bilirubin_mg_dl",
             "bclc_stage","afp_ng_ml","afp_ge_400","macrovascular_invasion",
             "extrahepatic_spread","varices_at_baseline","os_time_months","os_event",
             "pfs_time_months","pfs_event","best_overall_response","objective_response",
             "grade34_adverse_event","grade34_hypertension"]].copy()
    out.insert(2, "enroll_date", g["enroll_year"].astype(str) + "-" +
               g["enroll_month"].map(lambda m: f"{m:02d}"))
    out.to_csv(path, index=False)

def emit_beta(g, path):    # European units, M/F, treatment=, Yes/No, "NA" missing
    out = pd.DataFrame({
        "patient_id": g["patient_id"], "site_code": g["hospital_id"],
        "enroll_date": g["enroll_year"].astype(str) + "-" + g["enroll_month"].map(lambda m: f"{m:02d}"),
        "treatment": np.where(g["arm"] == "Atezo+Bev", "AtezoBev", "Sorafenib"),
        "age": g["age"], "sex": np.where(g["sex"] == "Male", "M", "F"),
        "etiology": g["etiology"], "ecog": g["ecog_ps"], "cp_score": g["child_pugh_score"],
        "albi_grade": g["albi_grade"],
        "albumin_g_L": np.round(g["albumin_g_dl"]*10, 0),           # g/L
        "bilirubin_umol_L": np.round(g["bilirubin_mg_dl"]*17.1, 1), # umol/L
        "bclc_stage": g["bclc_stage"], "afp": g["afp_ng_ml"],
        "afp_over_400": yn(g["afp_ge_400"]),
        "mvi": yn(g["macrovascular_invasion"]), "ehs": yn(g["extrahepatic_spread"]),
        "varices": yn(g["varices_at_baseline"]),
        "os_months": g["os_time_months"], "os_death": g["os_event"],
        "pfs_months": g["pfs_time_months"], "pfs_prog": g["pfs_event"],
        "recist": g["best_overall_response"], "responder": g["objective_response"],
        "ae_grade34": g["grade34_adverse_event"], "htn_grade34": g["grade34_hypertension"],
    })
    out.to_csv(path, index=False, na_rep="NA")

def emit_gamma(g, path):   # registry: 1/0 codes, no continuous AFP, CP as "A5"/"A6"
    out = pd.DataFrame({
        "record_id": g["patient_id"], "site": g["hospital_id"],
        "enroll_yr": g["enroll_year"],
        "regimen": np.where(g["arm"] == "Atezo+Bev", "A+B", "SOR"),
        "age": g["age"], "male": np.where(g["sex"] == "Male", 1, 0),
        "etiology": g["etiology"].str.lower(),          # 'hbv'/'hcv'/'nonviral'
        "performance_status": g["ecog_ps"],
        "child_pugh": "A" + g["child_pugh_score"].astype(str),   # 'A5' / 'A6'
        "albi": g["albi_grade"], "alb": g["albumin_g_dl"], "tbili": g["bilirubin_mg_dl"],
        "bclc": g["bclc_stage"], "afp_high": g["afp_ge_400"],    # NO continuous AFP
        "vascular_invasion": g["macrovascular_invasion"],
        "extrahepatic": g["extrahepatic_spread"], "esoph_varices": g["varices_at_baseline"],
        "time_os": g["os_time_months"], "event_os": g["os_event"],
        "time_pfs": g["pfs_time_months"], "event_pfs": g["pfs_event"],
        "recist": g["best_overall_response"], "orr": g["objective_response"],
        "gr34_ae": g["grade34_adverse_event"], "gr34_htn": g["grade34_hypertension"],
    })
    out.to_csv(path, index=False)

vendor = dict(zip(hosp["hospital_id"], hosp["ehr_vendor"]))
name   = dict(zip(hosp["hospital_id"], hosp["hospital_name"]))
emit = {"Alpha": emit_alpha, "Beta": emit_beta, "Gamma": emit_gamma}
for hidx, g in canon.groupby("hospital_id"):
    v = vendor[hidx]
    slug = name[hidx].replace(" ", "_")
    path = f"hospitals/{hidx}_{slug}.csv"
    emit[v](g.reset_index(drop=True), path)
    print(f"{path:<48} vendor={v:<6} n={len(g):>4}")

print(f"\nWrote 10 hospital files (total {N}) + hospitals_meta.csv + answer key.")
