"""
MedAI - Data Transformers
Feature engineering, encoding, and preprocessing for the diabetic dataset.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from etl.medical_codes import (
    classify_diagnosis,
    MEDICATION_COLUMNS,
    ADMISSION_TYPES,
    DISCHARGE_DISPOSITIONS,
)


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean raw diabetic data.
    - Remove duplicates based on encounter_id
    - Handle missing values
    - Remove deceased/hospice patients (discharge 11,13,14,19,20,21)
    """
    print("🧹 Cleaning data...")
    df = df.copy()

    # Remove duplicate encounters
    initial_count = len(df)
    df = df.drop_duplicates(subset=["encounter_id"])
    print(f"   Removed {initial_count - len(df)} duplicate encounters.")

    # Remove patients who died or went to hospice (can't be readmitted)
    deceased_codes = [11, 13, 14, 19, 20, 21]
    df = df[~df["discharge_disposition_id"].isin(deceased_codes)]
    print(f"   Removed deceased/hospice patients. Remaining: {len(df):,}")

    # Drop columns with very high missing rates or near-zero variance
    cols_to_drop = ["weight", "payer_code", "examide", "citoglipton"]
    df = df.drop(columns=[c for c in cols_to_drop if c in df.columns], errors="ignore")
    print(f"   Dropped high-missing columns: {cols_to_drop}")

    # Fill missing medical_specialty
    df["medical_specialty"] = df["medical_specialty"].fillna("Unknown")

    return df


def encode_target(df: pd.DataFrame) -> pd.DataFrame:
    """
    Encode the readmission target variable.
    - '<30' → 1 (readmitted within 30 days — high risk)
    - '>30' or 'NO' → 0 (not readmitted within 30 days)
    """
    df = df.copy()
    df["readmit_binary"] = (df["readmitted"] == "<30").astype(int)
    print(f"🎯 Target distribution:")
    print(f"   Readmitted <30 days: {df['readmit_binary'].sum():,}")
    print(f"   Not readmitted <30: {(df['readmit_binary'] == 0).sum():,}")
    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create new features for ML models.
    """
    df = df.copy()
    print("🔧 Engineering features...")

    # Age to numeric midpoint
    age_map = {
        "[0-10)": 5, "[10-20)": 15, "[20-30)": 25, "[30-40)": 35,
        "[40-50)": 45, "[50-60)": 55, "[60-70)": 65, "[70-80)": 75,
        "[80-90)": 85, "[90-100)": 95,
    }
    df["age_numeric"] = df["age"].map(age_map).fillna(55)

    # Diagnosis category features
    for diag_col in ["diag_1", "diag_2", "diag_3"]:
        df[f"{diag_col}_category"] = df[diag_col].astype(str).apply(classify_diagnosis)

    # Count active medications
    med_cols_in_df = [c for c in MEDICATION_COLUMNS if c in df.columns]
    df["active_med_count"] = df[med_cols_in_df].apply(
        lambda row: sum(1 for v in row if v not in ["No", "Steady", np.nan]), axis=1
    )

    # Total visits (outpatient + emergency + inpatient)
    df["total_visits"] = (
        df["number_outpatient"].fillna(0)
        + df["number_emergency"].fillna(0)
        + df["number_inpatient"].fillna(0)
    )

    # Medication change indicator
    df["med_change"] = (df["change"] == "Ch").astype(int)

    # Has diabetes medication
    df["has_diabetes_med"] = (df["diabetesMed"] == "Yes").astype(int)

    # Lab procedures intensity
    df["lab_intensity"] = pd.cut(
        df["num_lab_procedures"],
        bins=[0, 20, 40, 60, 80, 150],
        labels=[0, 1, 2, 3, 4],
    ).astype(float).fillna(0)

    # High-risk admission type (emergency or urgent)
    df["emergency_admission"] = df["admission_type_id"].isin([1, 2]).astype(int)

    # A1C test result encoding
    a1c_map = {"None": 0, "Norm": 1, ">7": 2, ">8": 3}
    df["a1c_numeric"] = df["A1Cresult"].map(a1c_map).fillna(0)

    # Glucose serum encoding
    glu_map = {"None": 0, "Norm": 1, ">200": 2, ">300": 3}
    df["glu_numeric"] = df["max_glu_serum"].map(glu_map).fillna(0)

    # Is diabetes primary diagnosis
    df["diabetes_primary"] = df["diag_1"].astype(str).str.startswith("250").astype(int)

    print(f"   Created {10} new features.")
    return df


def encode_categoricals(df: pd.DataFrame) -> pd.DataFrame:
    """Encode categorical variables for ML."""
    df = df.copy()
    print("🏷️  Encoding categorical variables...")

    # Label encode categorical columns
    label_cols = ["race", "gender", "medical_specialty"]
    label_encoders = {}

    for col in label_cols:
        if col in df.columns:
            le = LabelEncoder()
            df[col + "_encoded"] = le.fit_transform(df[col].astype(str))
            label_encoders[col] = le

    # Encode diagnosis categories
    for col in ["diag_1_category", "diag_2_category", "diag_3_category"]:
        if col in df.columns:
            le = LabelEncoder()
            df[col + "_encoded"] = le.fit_transform(df[col].astype(str))
            label_encoders[col] = le

    # Encode medication columns
    med_map = {"No": 0, "Steady": 1, "Up": 2, "Down": 3}
    med_cols_in_df = [c for c in MEDICATION_COLUMNS if c in df.columns]
    for col in med_cols_in_df:
        df[col + "_encoded"] = df[col].map(med_map).fillna(0).astype(int)

    return df


def get_ml_features() -> list:
    """Return the list of feature columns used for ML models."""
    return [
        "age_numeric",
        "time_in_hospital",
        "num_lab_procedures",
        "num_procedures",
        "num_medications",
        "number_outpatient",
        "number_emergency",
        "number_inpatient",
        "number_diagnoses",
        "active_med_count",
        "total_visits",
        "med_change",
        "has_diabetes_med",
        "lab_intensity",
        "emergency_admission",
        "a1c_numeric",
        "glu_numeric",
        "diabetes_primary",
        "race_encoded",
        "gender_encoded",
        "diag_1_category_encoded",
        "diag_2_category_encoded",
        "diag_3_category_encoded",
        "admission_type_id",
        "discharge_disposition_id",
        "admission_source_id",
    ]


def prepare_ml_dataset(df: pd.DataFrame) -> tuple:
    """
    Full preprocessing pipeline for ML.
    Returns (X, y, feature_names, scaler).
    """
    print("\n" + "=" * 60)
    print("[*] PREPARING ML DATASET")
    print("=" * 60)

    # Clean
    df = clean_data(df)

    # Encode target
    df = encode_target(df)

    # Engineer features
    df = engineer_features(df)

    # Encode categoricals
    df = encode_categoricals(df)

    # Select features
    feature_cols = get_ml_features()
    available_features = [c for c in feature_cols if c in df.columns]

    X = df[available_features].copy()
    y = df["readmit_binary"].copy()

    # Handle remaining NaN
    X = X.fillna(0)

    # Scale features
    scaler = StandardScaler()
    X_scaled = pd.DataFrame(
        scaler.fit_transform(X),
        columns=available_features,
        index=X.index,
    )

    print(f"\n📊 Final dataset: {X_scaled.shape[0]:,} samples, {X_scaled.shape[1]} features")
    print(f"   Target balance: {y.value_counts().to_dict()}")

    return X_scaled, y, available_features, scaler
