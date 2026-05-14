"""
MedAI - Patient API Endpoints
CRUD operations and search for patient records.
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional

from backend.api.auth import get_current_user
from backend.database.connection import get_db
from backend.database.models import Patient, Encounter, User

router = APIRouter(prefix="/api/patients", tags=["Patients"])


@router.get("")
async def list_patients(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    gender: Optional[str] = None,
    age: Optional[str] = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List patients with pagination and filtering."""
    query = db.query(Patient)

    if search:
        query = query.filter(Patient.patient_nbr.like(f"%{search}%"))
    if gender:
        query = query.filter(Patient.gender == gender)
    if age:
        query = query.filter(Patient.age == age)

    total = query.count()
    patients = query.offset((page - 1) * limit).limit(limit).all()

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit,
        "data": [
            {
                "id": p.id,
                "patient_nbr": p.patient_nbr,
                "race": p.race,
                "gender": p.gender,
                "age": p.age,
                "encounter_count": db.query(Encounter).filter(Encounter.patient_id == p.id).count(),
            }
            for p in patients
        ],
    }


@router.get("/{patient_id}")
async def get_patient(
    patient_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get patient details with encounters."""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    encounters = db.query(Encounter).filter(Encounter.patient_id == patient_id).all()

    return {
        "id": patient.id,
        "patient_nbr": patient.patient_nbr,
        "race": patient.race,
        "gender": patient.gender,
        "age": patient.age,
        "encounters": [
            {
                "id": e.id,
                "encounter_id": e.encounter_id,
                "admission_type_id": e.admission_type_id,
                "discharge_disposition_id": e.discharge_disposition_id,
                "time_in_hospital": e.time_in_hospital,
                "num_medications": e.num_medications,
                "num_lab_procedures": e.num_lab_procedures,
                "num_procedures": e.num_procedures,
                "number_diagnoses": e.number_diagnoses,
                "diag_1": e.diag_1,
                "diag_2": e.diag_2,
                "diag_3": e.diag_3,
                "readmitted": e.readmitted,
                "medications": e.medications,
            }
            for e in encounters
        ],
    }


@router.get("/stats/summary")
async def patient_stats(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get aggregate patient statistics."""
    total_patients = db.query(Patient).count()
    total_encounters = db.query(Encounter).count()
    gender_dist = dict(db.query(Patient.gender, func.count(Patient.id)).group_by(Patient.gender).all())
    age_dist = dict(db.query(Patient.age, func.count(Patient.id)).group_by(Patient.age).all())

    return {
        "total_patients": total_patients,
        "total_encounters": total_encounters,
        "gender_distribution": gender_dist,
        "age_distribution": age_dist,
    }
