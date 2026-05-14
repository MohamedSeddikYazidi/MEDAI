"""
MedAI - ETL Pipeline Orchestrator
Runs the complete ETL process: Load → Clean → Transform → Store.
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from etl.loaders import load_diabetic_data, get_dataset_stats
from etl.transformers import prepare_ml_dataset
from backend.database.connection import SessionLocal, engine
from backend.database.models import Patient, Encounter
from backend.database.init_db import init_database
from etl.medical_codes import MEDICATION_COLUMNS
import pandas as pd


def load_to_database(df: pd.DataFrame, batch_size: int = 1000):
    """Load cleaned data into the database."""
    print("\n[*] Loading data into database...")
    db = SessionLocal()

    try:
        # Check if data already loaded
        existing = db.query(Patient).count()
        if existing > 0:
            print(f"[i] {existing} patients already in database. Skipping load.")
            return

        # Get unique patients
        patient_cols = ["patient_nbr", "race", "gender", "age", "weight"]
        patients_df = df.drop_duplicates(subset=["patient_nbr"])[
            [c for c in patient_cols if c in df.columns]
        ]

        patient_map = {}
        count = 0
        for _, row in patients_df.iterrows():
            patient = Patient(
                patient_nbr=int(row["patient_nbr"]),
                race=str(row.get("race", "Unknown")),
                gender=str(row.get("gender", "Unknown")),
                age=str(row.get("age", "Unknown")),
                weight=str(row.get("weight", "Unknown")) if "weight" in row else None,
            )
            db.add(patient)
            patient_map[int(row["patient_nbr"])] = patient
            count += 1

            if count % batch_size == 0:
                db.flush()
                print(f"   Loaded {count:,} patients...")

        db.flush()
        print(f"[+] Loaded {count:,} unique patients.")

        # Load encounters
        count = 0
        for _, row in df.iterrows():
            patient = patient_map.get(int(row["patient_nbr"]))
            if not patient:
                continue

            # Collect medication data
            meds = {}
            for med_col in MEDICATION_COLUMNS:
                if med_col in df.columns:
                    val = row.get(med_col)
                    if pd.notna(val):
                        meds[med_col] = str(val)

            encounter = Encounter(
                encounter_id=int(row["encounter_id"]),
                patient_id=patient.id,
                admission_type_id=int(row["admission_type_id"]) if pd.notna(row.get("admission_type_id")) else None,
                discharge_disposition_id=int(row["discharge_disposition_id"]) if pd.notna(row.get("discharge_disposition_id")) else None,
                admission_source_id=int(row["admission_source_id"]) if pd.notna(row.get("admission_source_id")) else None,
                time_in_hospital=int(row["time_in_hospital"]) if pd.notna(row.get("time_in_hospital")) else None,
                payer_code=str(row["payer_code"]) if pd.notna(row.get("payer_code")) else None,
                medical_specialty=str(row["medical_specialty"]) if pd.notna(row.get("medical_specialty")) else None,
                num_lab_procedures=int(row["num_lab_procedures"]) if pd.notna(row.get("num_lab_procedures")) else None,
                num_procedures=int(row["num_procedures"]) if pd.notna(row.get("num_procedures")) else None,
                num_medications=int(row["num_medications"]) if pd.notna(row.get("num_medications")) else None,
                number_outpatient=int(row["number_outpatient"]) if pd.notna(row.get("number_outpatient")) else None,
                number_emergency=int(row["number_emergency"]) if pd.notna(row.get("number_emergency")) else None,
                number_inpatient=int(row["number_inpatient"]) if pd.notna(row.get("number_inpatient")) else None,
                diag_1=str(row["diag_1"]) if pd.notna(row.get("diag_1")) else None,
                diag_2=str(row["diag_2"]) if pd.notna(row.get("diag_2")) else None,
                diag_3=str(row["diag_3"]) if pd.notna(row.get("diag_3")) else None,
                number_diagnoses=int(row["number_diagnoses"]) if pd.notna(row.get("number_diagnoses")) else None,
                max_glu_serum=str(row["max_glu_serum"]) if pd.notna(row.get("max_glu_serum")) else None,
                a1c_result=str(row["A1Cresult"]) if pd.notna(row.get("A1Cresult")) else None,
                change=str(row["change"]) if pd.notna(row.get("change")) else None,
                diabetes_med=str(row["diabetesMed"]) if pd.notna(row.get("diabetesMed")) else None,
                readmitted=str(row["readmitted"]) if pd.notna(row.get("readmitted")) else None,
                medications=meds,
            )
            db.add(encounter)
            count += 1

            if count % batch_size == 0:
                db.flush()
                print(f"   Loaded {count:,} encounters...")

        db.commit()
        print(f"[+] Loaded {count:,} encounters.")

    except Exception as e:
        db.rollback()
        print(f"[!] Error loading data: {e}")
        raise
    finally:
        db.close()


def run_etl():
    """Run the complete ETL pipeline."""
    print("=" * 60)
    print("[*] MedAI ETL PIPELINE")
    print("=" * 60)

    # Step 1: Initialize database
    init_database()

    # Step 2: Load raw data
    df = load_diabetic_data()
    stats = get_dataset_stats(df)
    print(f"\n[*] Dataset Stats:")
    print(f"   Total records: {stats['total_records']:,}")
    print(f"   Unique patients: {stats['unique_patients']:,}")
    print(f"   Readmission dist: {stats['readmission_distribution']}")

    # Step 3: Load into database
    load_to_database(df)

    # Step 4: Prepare ML dataset (saves for model training)
    X, y, features, scaler = prepare_ml_dataset(df)

    print("\n" + "=" * 60)
    print("[+] ETL PIPELINE COMPLETE")
    print("=" * 60)

    return X, y, features, scaler


if __name__ == "__main__":
    run_etl()
