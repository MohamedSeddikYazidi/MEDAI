"""
MedAI - BI & Analytics Agent
Transforms medical data into actionable insights, KPIs, and chart specifications.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import json
import pandas as pd
from agents.base_agent import BaseAgent, AgentResponse
from agents.llm_provider import call_llm


class BIAgent(BaseAgent):
    """Agent for business intelligence and medical analytics."""

    def __init__(self):
        super().__init__(
            name="BI & Analytics Agent",
            description="Generates medical KPIs, analytics, and dashboard data."
        )
        self._data = None

    def _load_data(self):
        if self._data is None:
            try:
                from etl.loaders import load_diabetic_data
                self._data = load_diabetic_data()
            except Exception:
                self._data = pd.DataFrame()
        return self._data

    def get_capabilities(self) -> list[str]:
        return [
            "kpi_generation", "trend_analysis", "patient_segmentation",
            "dashboard_data", "statistical_analysis",
        ]

    async def process(self, input_data: dict) -> AgentResponse:
        """
        Generate BI analytics.
        Input: {"query_type": str, "filters": dict (optional)}
        """
        try:
            query_type = input_data.get("query_type", "executive_dashboard")
            filters = input_data.get("filters", {})

            df = self._load_data()
            if df.empty:
                return self._error_response("No data available for analysis.")

            handlers = {
                "executive_dashboard": self._executive_dashboard,
                "predictive_dashboard": self._predictive_dashboard,
                "clinical_dashboard": self._clinical_dashboard,
                "operational_dashboard": self._operational_dashboard,
                "kpis": self._get_kpis,
            }

            handler = handlers.get(query_type, self._executive_dashboard)
            result = handler(df, filters)

            return self._create_response(
                data=result,
                confidence=0.95,
                reasoning=f"Generated {query_type} analytics from {len(df):,} records.",
            )

        except Exception as e:
            return self._error_response(f"BI analysis error: {str(e)}")

    def _get_kpis(self, df: pd.DataFrame, filters: dict) -> dict:
        total = len(df)
        readmit_30 = (df["readmitted"] == "<30").sum()
        readmit_any = (df["readmitted"] != "NO").sum()

        return {
            "total_encounters": int(total),
            "unique_patients": int(df["patient_nbr"].nunique()),
            "readmission_rate_30day": round(readmit_30 / total * 100, 2),
            "readmission_rate_any": round(readmit_any / total * 100, 2),
            "avg_time_in_hospital": round(df["time_in_hospital"].mean(), 2),
            "avg_num_medications": round(df["num_medications"].mean(), 2),
            "avg_num_procedures": round(df["num_procedures"].mean(), 2),
            "avg_lab_procedures": round(df["num_lab_procedures"].mean(), 2),
            "avg_diagnoses": round(df["number_diagnoses"].mean(), 2),
            "emergency_rate": round((df["admission_type_id"] == 1).sum() / total * 100, 2),
            "diabetes_med_rate": round((df["diabetesMed"] == "Yes").sum() / total * 100, 2),
            "insulin_usage_rate": round((df["insulin"] != "No").sum() / total * 100, 2),
        }

    def _executive_dashboard(self, df: pd.DataFrame, filters: dict) -> dict:
        kpis = self._get_kpis(df, filters)

        # Readmission distribution
        readmit_dist = df["readmitted"].value_counts().to_dict()

        # Age distribution
        age_dist = df["age"].value_counts().sort_index().to_dict()

        # Gender distribution
        gender_dist = df["gender"].value_counts().to_dict()

        # Race distribution
        race_dist = df["race"].value_counts().to_dict()

        # Admission type distribution
        from etl.medical_codes import ADMISSION_TYPES
        admission_dist = {}
        for code, label in ADMISSION_TYPES.items():
            count = (df["admission_type_id"] == code).sum()
            if count > 0:
                admission_dist[label] = int(count)

        # Top diagnoses
        top_diag = df["diag_1"].value_counts().head(10).to_dict()

        return {
            "kpis": kpis,
            "charts": {
                "readmission_distribution": {"type": "donut", "data": readmit_dist},
                "age_distribution": {"type": "bar", "data": age_dist},
                "gender_distribution": {"type": "pie", "data": gender_dist},
                "race_distribution": {"type": "bar", "data": race_dist},
                "admission_type_distribution": {"type": "bar", "data": admission_dist},
                "top_diagnoses": {"type": "horizontal_bar", "data": {str(k): int(v) for k, v in top_diag.items()}},
            },
        }

    def _predictive_dashboard(self, df: pd.DataFrame, filters: dict) -> dict:
        # Risk segmentation
        df_copy = df.copy()
        df_copy["risk_category"] = "Low"
        df_copy.loc[df_copy["number_inpatient"] >= 1, "risk_category"] = "Medium"
        df_copy.loc[
            (df_copy["number_inpatient"] >= 2) | (df_copy["number_emergency"] >= 2),
            "risk_category"
        ] = "High"

        risk_dist = df_copy["risk_category"].value_counts().to_dict()

        # Readmission by age
        readmit_by_age = df.groupby("age")["readmitted"].apply(
            lambda x: round((x == "<30").sum() / len(x) * 100, 2)
        ).to_dict()

        # Readmission by admission type
        readmit_by_admission = df.groupby("admission_type_id")["readmitted"].apply(
            lambda x: round((x == "<30").sum() / len(x) * 100, 2)
        ).to_dict()
        readmit_by_admission = {str(k): v for k, v in readmit_by_admission.items()}

        # Medications vs readmission
        readmit_by_meds = df.groupby(pd.cut(df["num_medications"], bins=5))["readmitted"].apply(
            lambda x: round((x == "<30").sum() / len(x) * 100, 2)
        )
        med_readmit = {str(k): v for k, v in readmit_by_meds.items()}

        # Hospital stay vs readmission
        stay_readmit = df.groupby(pd.cut(df["time_in_hospital"], bins=5))["readmitted"].apply(
            lambda x: round((x == "<30").sum() / len(x) * 100, 2)
        )
        stay_data = {str(k): v for k, v in stay_readmit.items()}

        return {
            "risk_distribution": {"type": "donut", "data": risk_dist},
            "readmission_by_age": {"type": "line", "data": readmit_by_age},
            "readmission_by_admission_type": {"type": "bar", "data": readmit_by_admission},
            "readmission_by_medications": {"type": "bar", "data": med_readmit},
            "readmission_by_stay": {"type": "line", "data": stay_data},
            "high_risk_count": int((df_copy["risk_category"] == "High").sum()),
            "medium_risk_count": int((df_copy["risk_category"] == "Medium").sum()),
            "low_risk_count": int((df_copy["risk_category"] == "Low").sum()),
        }

    def _clinical_dashboard(self, df: pd.DataFrame, filters: dict) -> dict:
        # Top medical specialties
        specialty_dist = df["medical_specialty"].value_counts().head(10).to_dict()
        specialty_dist = {str(k): int(v) for k, v in specialty_dist.items()}

        # A1C results
        a1c_dist = df["A1Cresult"].value_counts().to_dict()

        # Glucose serum
        glu_dist = df["max_glu_serum"].value_counts().to_dict()

        # Insulin usage
        insulin_dist = df["insulin"].value_counts().to_dict()

        # Metformin usage
        metformin_dist = df["metformin"].value_counts().to_dict()

        # Medication changes
        change_dist = df["change"].value_counts().to_dict()

        # Procedures distribution
        proc_stats = {
            "mean": round(df["num_procedures"].mean(), 2),
            "median": round(df["num_procedures"].median(), 2),
            "max": int(df["num_procedures"].max()),
        }

        return {
            "charts": {
                "top_specialties": {"type": "horizontal_bar", "data": specialty_dist},
                "a1c_results": {"type": "donut", "data": a1c_dist},
                "glucose_serum": {"type": "donut", "data": glu_dist},
                "insulin_usage": {"type": "bar", "data": insulin_dist},
                "metformin_usage": {"type": "bar", "data": metformin_dist},
                "medication_changes": {"type": "pie", "data": change_dist},
            },
            "procedure_stats": proc_stats,
        }

    def _operational_dashboard(self, df: pd.DataFrame, filters: dict) -> dict:
        # Hospital stay distribution
        stay_dist = df["time_in_hospital"].value_counts().sort_index().to_dict()
        stay_dist = {str(k): int(v) for k, v in stay_dist.items()}

        # Discharge disposition
        from etl.medical_codes import DISCHARGE_DISPOSITIONS
        discharge_dist = {}
        for code, label in DISCHARGE_DISPOSITIONS.items():
            count = (df["discharge_disposition_id"] == code).sum()
            if count > 100:
                discharge_dist[label[:30]] = int(count)

        # Workload by specialty
        workload = df["medical_specialty"].value_counts().head(8).to_dict()
        workload = {str(k): int(v) for k, v in workload.items()}

        # High-priority patients
        high_priority = df[
            (df["number_emergency"] >= 2) | (df["number_inpatient"] >= 3)
        ]

        return {
            "charts": {
                "stay_distribution": {"type": "bar", "data": stay_dist},
                "discharge_disposition": {"type": "horizontal_bar", "data": discharge_dist},
                "workload_by_specialty": {"type": "bar", "data": workload},
            },
            "alerts": {
                "high_priority_patients": int(len(high_priority)),
                "long_stay_patients": int((df["time_in_hospital"] >= 10).sum()),
                "frequent_readmissions": int(df[df["number_inpatient"] >= 3]["patient_nbr"].nunique()),
            },
        }
