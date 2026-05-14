"""
MedAI - ICD-10 Medical Code Mappings
Maps diagnosis codes from the dataset to human-readable descriptions and categories.
"""

# ICD-10 Diagnosis Code Groups
# Based on standard ICD-10 ranges
ICD10_CATEGORIES = {
    "Infectious": (1, 139),
    "Neoplasms": (140, 239),
    "Endocrine/Metabolic": (240, 279),
    "Blood Diseases": (280, 289),
    "Mental Disorders": (290, 319),
    "Nervous System": (320, 389),
    "Circulatory": (390, 459),
    "Respiratory": (460, 519),
    "Digestive": (520, 579),
    "Genitourinary": (580, 629),
    "Pregnancy": (630, 679),
    "Skin/Subcutaneous": (680, 709),
    "Musculoskeletal": (710, 739),
    "Congenital": (740, 759),
    "Perinatal": (760, 779),
    "Ill-defined": (780, 799),
    "Injury/Poisoning": (800, 999),
}

# Diabetes-specific ICD-10 codes (250.xx)
DIABETES_CODES = {
    "250.00": "Diabetes mellitus type II, not stated, not uncontrolled",
    "250.01": "Diabetes mellitus type I, not stated, not uncontrolled",
    "250.02": "Diabetes mellitus type II, not stated, uncontrolled",
    "250.03": "Diabetes mellitus type I, not stated, uncontrolled",
    "250.10": "Diabetes with ketoacidosis, type II",
    "250.11": "Diabetes with ketoacidosis, type I",
    "250.12": "Diabetes with ketoacidosis, type II, uncontrolled",
    "250.13": "Diabetes with ketoacidosis, type I, uncontrolled",
    "250.20": "Diabetes with hyperosmolarity, type II",
    "250.21": "Diabetes with hyperosmolarity, type I",
    "250.30": "Diabetes with other coma, type II",
    "250.40": "Diabetes with renal manifestations, type II",
    "250.41": "Diabetes with renal manifestations, type I",
    "250.50": "Diabetes with ophthalmic manifestations, type II",
    "250.60": "Diabetes with neurological manifestations, type II",
    "250.70": "Diabetes with peripheral circulatory disorders, type II",
    "250.80": "Diabetes with other specified manifestations, type II",
    "250.83": "Diabetes with other specified manifestations, type I, not uncontrolled",
    "250.90": "Diabetes with unspecified complication, type II",
}

# Admission Type Mapping
ADMISSION_TYPES = {
    1: "Emergency",
    2: "Urgent",
    3: "Elective",
    4: "Newborn",
    5: "Not Available",
    6: "NULL",
    7: "Trauma Center",
    8: "Not Mapped",
}

# Discharge Disposition Mapping
DISCHARGE_DISPOSITIONS = {
    1: "Discharged to home",
    2: "Transferred to short-term hospital",
    3: "Transferred to SNF",
    5: "Transferred to other type of institution",
    6: "Discharged to home with home health service",
    7: "Left AMA",
    8: "Discharged to home with IV provider",
    9: "Admitted as inpatient",
    10: "Neonate transferred",
    11: "Expired",
    12: "Still patient",
    13: "Hospice / home",
    14: "Hospice / medical facility",
    15: "Transferred within this institution",
    18: "NULL",
    19: "Expired at home (Medicaid only)",
    20: "Expired (Medicaid only)",
    21: "Expired (Medicare only)",
    22: "Transferred to rehab facility",
    23: "Transferred to long-term care hospital",
    24: "Transferred to nursing facility (Medicaid)",
    25: "Not Mapped",
    26: "Unknown",
    27: "Transferred to psychiatric hospital",
    28: "Transferred to critical access hospital",
    29: "Transferred to another facility",
    30: "Transferred to federal health care facility",
}

# Admission Source Mapping
ADMISSION_SOURCES = {
    1: "Physician Referral",
    2: "Clinic Referral",
    3: "HMO Referral",
    4: "Transfer from a hospital",
    5: "Transfer from a SNF",
    6: "Transfer from another facility",
    7: "Emergency Room",
    8: "Court/Law Enforcement",
    9: "Not Available",
    10: "Transfer from critical access hospital",
    11: "Normal Delivery",
    12: "Premature Delivery",
    13: "Sick Baby",
    14: "Extramural Birth",
    17: "NULL",
    20: "Not Mapped",
    22: "Transfer from hospital inpatient to Medicare",
    25: "Transfer from Ambulatory Surgery Center",
}

# Medication names in the dataset
MEDICATION_COLUMNS = [
    "metformin", "repaglinide", "nateglinide", "chlorpropamide",
    "glimepiride", "acetohexamide", "glipizide", "glyburide",
    "tolbutamide", "pioglitazone", "rosiglitazone", "acarbose",
    "miglitol", "troglitazone", "tolazamide", "examide",
    "citoglipton", "insulin", "glyburide-metformin",
    "glipizide-metformin", "glimepiride-pioglitazone",
    "metformin-rosiglitazone", "metformin-pioglitazone",
]


def classify_diagnosis(code_str: str) -> str:
    """Classify a diagnosis code string into a category."""
    if not code_str or code_str == "?" or code_str == "nan":
        return "Unknown"

    # Handle V-codes (supplementary)
    if str(code_str).startswith("V"):
        return "Supplementary"

    # Handle E-codes (external causes)
    if str(code_str).startswith("E"):
        return "External Causes"

    try:
        code_num = float(str(code_str).split(".")[0])
        for category, (low, high) in ICD10_CATEGORIES.items():
            if low <= code_num <= high:
                return category
        return "Other"
    except (ValueError, TypeError):
        return "Unknown"


def get_diagnosis_description(code_str: str) -> str:
    """Get human-readable description for a diagnosis code."""
    if code_str in DIABETES_CODES:
        return DIABETES_CODES[code_str]
    category = classify_diagnosis(code_str)
    return f"{category} condition (ICD: {code_str})"
