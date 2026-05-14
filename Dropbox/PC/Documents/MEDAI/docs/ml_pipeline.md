# MedAI — ML Pipeline Documentation

## Overview

The ML pipeline trains 4 models on the diabetic_data.csv dataset (101,766 records) to predict 30-day hospital readmission.

## Dataset

| Property | Value |
|----------|-------|
| Source | diabetic_data.csv |
| Records | 101,766 encounters |
| Unique Patients | ~71,518 |
| Features | 50 raw columns |
| Target | `readmitted` (binary: <30 days = 1) |

## Preprocessing Pipeline

### 1. Data Cleaning
- Remove duplicate encounters
- Remove deceased/hospice patients (can't be readmitted)
- Drop high-missing columns: weight, payer_code, examide, citoglipton
- Fill missing medical_specialty with "Unknown"

### 2. Feature Engineering (26 features)

| Feature | Description |
|---------|-------------|
| `age_numeric` | Age range midpoint |
| `time_in_hospital` | Length of stay |
| `num_lab_procedures` | Lab tests count |
| `num_procedures` | Procedures count |
| `num_medications` | Active medications |
| `number_outpatient` | Prior outpatient visits |
| `number_emergency` | Prior emergency visits |
| `number_inpatient` | Prior inpatient visits |
| `number_diagnoses` | Diagnosis count |
| `active_med_count` | Changed medications count |
| `total_visits` | Sum of all prior visits |
| `med_change` | Binary: medication changed |
| `has_diabetes_med` | Binary: on diabetes medication |
| `lab_intensity` | Lab procedures binned (0-4) |
| `emergency_admission` | Binary: emergency/urgent admission |
| `a1c_numeric` | A1C result encoded (0-3) |
| `glu_numeric` | Glucose serum encoded (0-3) |
| `diabetes_primary` | Binary: primary diagnosis is diabetes |
| `race_encoded` | Race label encoded |
| `gender_encoded` | Gender label encoded |
| `diag_*_category_encoded` | ICD-10 category encoded (3 features) |
| `admission_type_id` | Admission type |
| `discharge_disposition_id` | Discharge type |
| `admission_source_id` | Admission source |

### 3. Class Balancing
- SMOTE (Synthetic Minority Over-sampling Technique)
- Balances readmitted (<30) vs not readmitted classes

### 4. Feature Scaling
- StandardScaler on all features

## Models

| Model | Library | Key Hyperparameters |
|-------|---------|-------------------|
| XGBoost | xgboost | n_estimators, max_depth, learning_rate |
| Random Forest | sklearn | n_estimators, max_depth, min_samples_split |
| LightGBM | lightgbm | n_estimators, max_depth, num_leaves |
| Logistic Regression | sklearn | C, penalty, solver |

## Training Process
1. Stratified 80/20 train/test split
2. SMOTE on training set only
3. 5-fold stratified cross-validation
4. GridSearchCV for hyperparameter tuning
5. Evaluation on held-out test set

## Evaluation Metrics
- Accuracy
- Precision
- Recall
- F1 Score
- ROC AUC
- Confusion Matrix

## Explainability (XAI)
- **SHAP (SHapley Additive exPlanations)**
- TreeExplainer for tree-based models
- LinearExplainer for logistic regression
- Per-prediction feature contribution
- Summary and bar plots generated

## Generated Outputs
- `models/saved_models/{model}_model.joblib` — Serialized models
- `models/saved_models/{model}_metrics.json` — Performance metrics
- `models/saved_models/scaler.joblib` — Feature scaler
- `models/saved_models/feature_names.json` — Feature list
- `models/saved_models/best_model.json` — Best model indicator
- `models/saved_models/plots/` — ROC curves, confusion matrices, feature importance, SHAP plots
