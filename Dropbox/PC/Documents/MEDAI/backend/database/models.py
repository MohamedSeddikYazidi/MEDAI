"""
MedAI - Database ORM Models
All database models for the medical platform.
"""

import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text,
    ForeignKey, JSON, Enum as SAEnum
)
from sqlalchemy.orm import relationship
from backend.database.connection import Base
import enum


def generate_uuid():
    return str(uuid.uuid4())


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    DOCTOR = "doctor"
    NURSE = "nurse"
    ANALYST = "analyst"


class User(Base):
    """User model for authentication and authorization."""
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(20), default=UserRole.DOCTOR)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    audit_logs = relationship("AuditLog", back_populates="user")
    sessions = relationship("ChatSession", back_populates="user")


class Patient(Base):
    """Patient record model."""
    __tablename__ = "patients"

    id = Column(String, primary_key=True, default=generate_uuid)
    patient_nbr = Column(Integer, unique=True, index=True)
    race = Column(String(50))
    gender = Column(String(20))
    age = Column(String(20))
    weight = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    encounters = relationship("Encounter", back_populates="patient")
    predictions = relationship("Prediction", back_populates="patient")


class Encounter(Base):
    """Medical encounter/visit record."""
    __tablename__ = "encounters"

    id = Column(String, primary_key=True, default=generate_uuid)
    encounter_id = Column(Integer, unique=True, index=True)
    patient_id = Column(String, ForeignKey("patients.id"), nullable=False)
    admission_type_id = Column(Integer)
    discharge_disposition_id = Column(Integer)
    admission_source_id = Column(Integer)
    time_in_hospital = Column(Integer)
    payer_code = Column(String(10))
    medical_specialty = Column(String(100))
    num_lab_procedures = Column(Integer)
    num_procedures = Column(Integer)
    num_medications = Column(Integer)
    number_outpatient = Column(Integer)
    number_emergency = Column(Integer)
    number_inpatient = Column(Integer)
    diag_1 = Column(String(20))
    diag_2 = Column(String(20))
    diag_3 = Column(String(20))
    number_diagnoses = Column(Integer)
    max_glu_serum = Column(String(20))
    a1c_result = Column(String(20))
    change = Column(String(10))
    diabetes_med = Column(String(10))
    readmitted = Column(String(10))

    # Medication fields stored as JSON
    medications = Column(JSON)

    # Relationships
    patient = relationship("Patient", back_populates="encounters")
    created_at = Column(DateTime, default=datetime.utcnow)


class Prediction(Base):
    """ML prediction results."""
    __tablename__ = "predictions"

    id = Column(String, primary_key=True, default=generate_uuid)
    patient_id = Column(String, ForeignKey("patients.id"), nullable=False)
    model_name = Column(String(50), nullable=False)
    prediction_type = Column(String(50), nullable=False)  # readmission, risk, etc.
    probability = Column(Float)
    prediction = Column(Integer)  # 0 or 1
    confidence = Column(Float)
    feature_importance = Column(JSON)  # SHAP values
    explanation = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    patient = relationship("Patient", back_populates="predictions")


class DiagnosisResult(Base):
    """Agent diagnostic results."""
    __tablename__ = "diagnosis_results"

    id = Column(String, primary_key=True, default=generate_uuid)
    session_id = Column(String, ForeignKey("chat_sessions.id"))
    symptoms_input = Column(Text)
    extracted_entities = Column(JSON)  # NER results
    diagnoses = Column(JSON)  # List of {diagnosis, confidence, reasoning}
    risk_assessment = Column(JSON)
    treatment_recommendations = Column(JSON)
    sources = Column(JSON)  # RAG sources cited
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("ChatSession", back_populates="diagnoses")


class ChatSession(Base):
    """Medical chat session."""
    __tablename__ = "chat_sessions"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String(255))
    status = Column(String(20), default="active")  # active, closed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="sessions")
    messages = relationship("ChatMessage", back_populates="session")
    diagnoses = relationship("DiagnosisResult", back_populates="session")


class ChatMessage(Base):
    """Individual chat message."""
    __tablename__ = "chat_messages"

    id = Column(String, primary_key=True, default=generate_uuid)
    session_id = Column(String, ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    agent_name = Column(String(50))  # Which agent responded
    meta_data = Column(JSON)  # Additional data (sources, confidence, etc.)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("ChatSession", back_populates="messages")


class AuditLog(Base):
    """Audit trail for compliance."""
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"))
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50))
    resource_id = Column(String)
    details = Column(JSON)
    ip_address = Column(String(45))
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="audit_logs")


class MedicalDocument(Base):
    """Tracked medical documents for RAG."""
    __tablename__ = "medical_documents"

    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String(500), nullable=False)
    source = Column(String(500))
    doc_type = Column(String(50))  # guideline, article, protocol
    content_hash = Column(String(64))
    chunk_count = Column(Integer, default=0)
    ingested_at = Column(DateTime, default=datetime.utcnow)
    meta_data = Column(JSON)
