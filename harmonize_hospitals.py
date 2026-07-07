"""
Reference harmoniser: read the 10 dialect files in hospitals/, map each vendor
to one common schema, and pool them. This is the answer key for the "combine 10
hospitals" step -- in the live demo the agent writes its own version.

Returns a single tidy DataFrame with canonical columns. Run directly to write
imbrave150_pooled.csv and validate it against _answer_key_pooled.csv.
"""
import glob
import numpy as np
import pandas as pd

CANON_COLS = ["patient_id","hospital_id","enroll_year","arm","age","sex","etiology",
              "ecog_ps","child_pugh_score","albi_grade","albumin_g_dl","bilirubin_mg_dl",
              "bclc_stage","afp_ng_ml","afp_ge_400","macrovascular_invasion",
              "extrahepatic_spread","varices_at_baseline","os_time_months","os_event",
              "pfs_time_months","pfs_event","best_overall_response","objective_response",
              "grade34_adverse_event","grade34_hypertension"]

def _yn_to01(s):
    return s.map({"Yes": 1, "No": 0}).astype("Float64")

def _detect_vendor(cols):
    cols = set(cols)
    if {"regimen", "male", "afp_high"} & cols:       return "Gamma"
    if {"treatment", "albumin_g_L", "os_death"} & cols: return "Beta"
    return "Alpha"

def harmonise_file(path):
    df = pd.read_csv(path, na_values=["NA", "unknown", ""])
    v = _detect_vendor(df.columns)
    if v == "Alpha":
        df = df.rename(columns={})
        df["enroll_year"] = df["enroll_date"].astype(str).str[:4].astype(int)
    elif v == "Beta":
        df = df.rename(columns={
            "site_code":"hospital_id","treatment":"arm","ecog":"ecog_ps",
            "cp_score":"child_pugh_score","afp":"afp_ng_ml","os_months":"os_time_months",
            "os_death":"os_event","pfs_months":"pfs_time_months","pfs_prog":"pfs_event",
            "recist":"best_overall_response","responder":"objective_response",
            "ae_grade34":"grade34_adverse_event","htn_grade34":"grade34_hypertension"})
        df["arm"] = df["arm"].map({"AtezoBev":"Atezo+Bev","Sorafenib":"Sorafenib"})
        df["sex"] = df["sex"].map({"M":"Male","F":"Female"})
        df["albumin_g_dl"] = df["albumin_g_L"] / 10.0
        df["bilirubin_mg_dl"] = df["bilirubin_umol_L"] / 17.1
        df["afp_ge_400"] = _yn_to01(df["afp_over_400"])
        df["macrovascular_invasion"] = _yn_to01(df["mvi"])
        df["extrahepatic_spread"] = _yn_to01(df["ehs"])
        df["varices_at_baseline"] = _yn_to01(df["varices"])
        df["enroll_year"] = df["enroll_date"].astype(str).str[:4].astype(int)
    else:  # Gamma
        df = df.rename(columns={
            "record_id":"patient_id","site":"hospital_id","enroll_yr":"enroll_year",
            "regimen":"arm","performance_status":"ecog_ps","albi":"albi_grade",
            "alb":"albumin_g_dl","tbili":"bilirubin_mg_dl","bclc":"bclc_stage",
            "afp_high":"afp_ge_400","vascular_invasion":"macrovascular_invasion",
            "extrahepatic":"extrahepatic_spread","esoph_varices":"varices_at_baseline",
            "time_os":"os_time_months","event_os":"os_event","time_pfs":"pfs_time_months",
            "event_pfs":"pfs_event","recist":"best_overall_response","orr":"objective_response",
            "gr34_ae":"grade34_adverse_event","gr34_htn":"grade34_hypertension"})
        df["arm"] = df["arm"].map({"A+B":"Atezo+Bev","SOR":"Sorafenib"})
        df["sex"] = df["male"].map({1:"Male",0:"Female"})
        df["etiology"] = df["etiology"].str.upper().replace({"NONVIRAL":"Nonviral"})
        df["child_pugh_score"] = df["child_pugh"].str[1:].astype(int)
        df["afp_ng_ml"] = np.nan                      # registry kept only the threshold
    df["ehr_vendor"] = v
    for c in CANON_COLS:
        if c not in df.columns:
            df[c] = np.nan
    return df[CANON_COLS + ["ehr_vendor"]]

def load_pooled(folder="hospitals"):
    files = sorted(glob.glob(f"{folder}/*.csv"))
    return pd.concat([harmonise_file(f) for f in files], ignore_index=True)

if __name__ == "__main__":
    pooled = load_pooled()
    pooled.to_csv("imbrave150_pooled.csv", index=False)
    print(f"Harmonised {pooled['hospital_id'].nunique()} hospitals -> "
          f"{len(pooled)} patients, {pooled.shape[1]} cols")
    # validate against answer key on the columns that must round-trip exactly
    key = pd.read_csv("_answer_key_pooled.csv").sort_values("patient_id").reset_index(drop=True)
    got = pooled.sort_values("patient_id").reset_index(drop=True)
    check = ["arm","age","sex","ecog_ps","child_pugh_score","afp_ge_400",
             "macrovascular_invasion","extrahepatic_spread","varices_at_baseline",
             "os_time_months","os_event","pfs_time_months","pfs_event"]
    ok = all((key[c].fillna(-999) == got[c].fillna(-999)).all() for c in check)
    print("Round-trip validation vs answer key:", "PASS" if ok else "FAIL")
