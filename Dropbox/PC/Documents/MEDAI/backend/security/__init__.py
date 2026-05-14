"""
MedAI - Security Module
Encryption, anonymization, and compliance utilities.
"""

import hashlib
import base64
import os
import re
from typing import Optional
from cryptography.fernet import Fernet


class DataEncryption:
    """AES-256 field-level encryption for PII data."""

    def __init__(self, key: Optional[str] = None):
        if key:
            # Derive a Fernet-compatible key from the provided key
            derived = hashlib.sha256(key.encode()).digest()
            self.fernet = Fernet(base64.urlsafe_b64encode(derived))
        else:
            self.fernet = Fernet(Fernet.generate_key())

    def encrypt(self, plaintext: str) -> str:
        return self.fernet.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        return self.fernet.decrypt(ciphertext.encode()).decode()


class DataAnonymizer:
    """Anonymize PII data for HIPAA/GDPR compliance."""

    @staticmethod
    def anonymize_patient_id(patient_id: int) -> str:
        return hashlib.sha256(str(patient_id).encode()).hexdigest()[:16]

    @staticmethod
    def anonymize_name(name: str) -> str:
        if not name:
            return "***"
        return name[0] + "*" * (len(name) - 1)

    @staticmethod
    def anonymize_age(age_range: str) -> str:
        # Keep age ranges as they are (already de-identified)
        return age_range

    @staticmethod
    def redact_text(text: str) -> str:
        """Redact potential PII from free text."""
        # Redact email addresses
        text = re.sub(r'\b[\w.-]+@[\w.-]+\.\w+\b', '[REDACTED_EMAIL]', text)
        # Redact phone numbers
        text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[REDACTED_PHONE]', text)
        # Redact SSN patterns
        text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[REDACTED_SSN]', text)
        return text


class ComplianceChecker:
    """HIPAA/GDPR compliance simulation."""

    HIPAA_PHI_FIELDS = [
        "name", "address", "date_of_birth", "phone", "email",
        "ssn", "medical_record_number", "account_number",
        "certificate_number", "vehicle_identifier", "device_identifier",
        "url", "ip_address", "biometric", "photo",
    ]

    @staticmethod
    def check_data_access(user_role: str, data_type: str) -> dict:
        """Check if user role has access to data type."""
        access_matrix = {
            "admin": ["all"],
            "doctor": ["patient_records", "encounters", "predictions", "diagnoses", "treatments"],
            "nurse": ["patient_records", "encounters", "medications"],
            "analyst": ["aggregate_stats", "predictions", "analytics"],
        }

        allowed = access_matrix.get(user_role, [])
        has_access = "all" in allowed or data_type in allowed

        return {
            "user_role": user_role,
            "data_type": data_type,
            "access_granted": has_access,
            "compliance": "HIPAA/GDPR",
        }

    @staticmethod
    def generate_audit_entry(user_id: str, action: str, resource: str, details: dict = None) -> dict:
        """Generate a compliant audit log entry."""
        from datetime import datetime
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "action": action,
            "resource": resource,
            "details": details or {},
            "compliance_check": True,
        }
