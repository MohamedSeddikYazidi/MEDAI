"""
MedAI - BI ETL Script
Generates BI-ready analytical tables and exports for dashboards.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import json
from etl.loaders import load_diabetic_data
from etl.medical_codes import classify_diagnosis, ADMISSION_TYPES, DISCHARGE_DISPOSITIONS


def generate_bi_tables():
    """Generate BI-optimized analytical tables."""
    print("=" * 60)
    print("[*] MedAI BI ETL - Generating Analytical Tables")
    print("=" * 60)

    df = load_diabetic_data()

    output_dir = Path(__file__).parent / "exports"
    output_dir.mkdir(exist_ok=True)

    # 1. Patient Summary Table
    print("\n[*] Generating patient summary table...")
    patients = df.groupby("patient_nbr").agg(
        total_encounters=("encounter_id", "count"),
        avg_time_in_hospital=("time_in_hospital", "mean"),
        total_medications=("num_medications", "sum"),
        readmit_count=("readmitted", lambda x: (x == "<30").sum()),
        race=("race", "first"),
        gender=("gender", "first"),
        age=("age", "first"),
    ).reset_index()
    patients["readmission_rate"] = patients["readmit_count"] / patients["total_encounters"]
    patients.to_csv(output_dir / "patient_summary.csv", index=False)
    print(f"   Saved {len(patients)} patient summaries.")

    # 2. Diagnosis Analytics
    print("\n[*] Generating diagnosis analytics...")
    df["diag_1_category"] = df["diag_1"].astype(str).apply(classify_diagnosis)
    diag_stats = df.groupby("diag_1_category").agg(
        total_encounters=("encounter_id", "count"),
        avg_stay=("time_in_hospital", "mean"),
        readmission_rate=("readmitted", lambda x: (x == "<30").sum() / len(x) * 100),
    ).reset_index().sort_values("total_encounters", ascending=False)
    diag_stats.to_csv(output_dir / "diagnosis_analytics.csv", index=False)
    print(f"   Saved {len(diag_stats)} diagnosis categories.")

    # 3. Medication Effectiveness
    print("\n[*] Generating medication analytics...")
    med_cols = ["metformin", "insulin", "glipizide", "glyburide", "pioglitazone"]
    med_stats = []
    for med in med_cols:
        if med in df.columns:
            for status in df[med].unique():
                subset = df[df[med] == status]
                med_stats.append({
                    "medication": med,
                    "status": status,
                    "count": len(subset),
                    "readmission_rate": (subset["readmitted"] == "<30").sum() / len(subset) * 100 if len(subset) > 0 else 0,
                    "avg_stay": subset["time_in_hospital"].mean(),
                })
    pd.DataFrame(med_stats).to_csv(output_dir / "medication_analytics.csv", index=False)

    # 4. Time Series (simulated monthly trends from encounter data)
    print("\n[*] Generating KPI summary...")
    kpi_summary = {
        "total_encounters": int(len(df)),
        "unique_patients": int(df["patient_nbr"].nunique()),
        "readmission_rate_30day": round((df["readmitted"] == "<30").sum() / len(df) * 100, 2),
        "readmission_rate_any": round((df["readmitted"] != "NO").sum() / len(df) * 100, 2),
        "avg_time_in_hospital": round(df["time_in_hospital"].mean(), 2),
        "avg_medications": round(df["num_medications"].mean(), 2),
        "avg_procedures": round(df["num_procedures"].mean(), 2),
        "avg_lab_procedures": round(df["num_lab_procedures"].mean(), 2),
        "emergency_admission_rate": round((df["admission_type_id"] == 1).sum() / len(df) * 100, 2),
        "diabetes_med_rate": round((df["diabetesMed"] == "Yes").sum() / len(df) * 100, 2),
    }
    with open(output_dir / "kpi_summary.json", "w") as f:
        json.dump(kpi_summary, f, indent=2)

    print(f"\n[+] BI ETL complete! Files saved to: {output_dir}")
    return kpi_summary


if __name__ == "__main__":
    generate_bi_tables()
