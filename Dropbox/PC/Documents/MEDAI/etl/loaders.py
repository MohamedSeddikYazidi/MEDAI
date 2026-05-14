"""
MedAI - Data Loaders
Load and parse the diabetic dataset and other data sources.
"""

import pandas as pd
from pathlib import Path
from backend.config import settings


def load_diabetic_data(filepath: str = None) -> pd.DataFrame:
    """
    Load the diabetic_data.csv dataset.
    
    Args:
        filepath: Optional path override. Defaults to settings.DATASET_PATH.
    
    Returns:
        Raw DataFrame with all columns.
    """
    path = filepath or settings.DATASET_PATH
    print(f"[*] Loading dataset from: {path}")

    df = pd.read_csv(
        path,
        na_values=["?"],
        low_memory=False,
    )

    print(f"[+] Loaded {len(df):,} records with {len(df.columns)} columns.")
    print(f"   Columns: {list(df.columns)}")
    return df


def get_dataset_stats(df: pd.DataFrame) -> dict:
    """Get basic statistics about the dataset."""
    return {
        "total_records": len(df),
        "total_columns": len(df.columns),
        "missing_values": df.isnull().sum().to_dict(),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "unique_patients": df["patient_nbr"].nunique(),
        "readmission_distribution": df["readmitted"].value_counts().to_dict(),
        "age_distribution": df["age"].value_counts().to_dict(),
        "gender_distribution": df["gender"].value_counts().to_dict(),
        "race_distribution": df["race"].value_counts().to_dict(),
    }


if __name__ == "__main__":
    df = load_diabetic_data()
    stats = get_dataset_stats(df)
    for key, value in stats.items():
        print(f"\n{key}: {value}")
