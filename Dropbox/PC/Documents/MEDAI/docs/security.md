# MedAI — Security & Compliance Documentation

## Overview

MedAI implements security controls aligned with HIPAA and GDPR requirements for healthcare data protection.

## Authentication

### JWT Token Architecture
- **Access Token**: Short-lived (30 minutes), used for API authorization
- **Refresh Token**: Long-lived (7 days), used to obtain new access tokens
- **Algorithm**: HS256 (HMAC-SHA256)

### Role-Based Access Control (RBAC)

| Role | Capabilities |
|------|-------------|
| **Admin** | Full system access, user management, audit logs |
| **Doctor** | Patient records, diagnoses, predictions, treatments |
| **Nurse** | Patient records, encounters, medications |
| **Analyst** | Aggregate statistics, predictions, analytics dashboards |

## Data Protection

### Encryption
- **At-rest**: AES-256 field-level encryption for PII
- **In-transit**: HTTPS (via reverse proxy in production)
- **Key management**: Environment variable-based (production: use a KMS)

### PII Anonymization
- Patient IDs hashed with SHA-256
- Names redacted in exports
- Email, phone, SSN patterns auto-redacted from free text

### Data Minimization
- Only essential patient data stored
- Age stored as ranges (not dates of birth)
- No direct identifiers in ML training data

## Compliance

### HIPAA Alignment
- ✅ Access controls (RBAC)
- ✅ Audit trail (all data access logged)
- ✅ Encryption (AES-256 at rest)
- ✅ Minimum necessary access
- ✅ Data integrity controls

### GDPR Alignment
- ✅ Lawful basis for processing (healthcare)
- ✅ Data minimization
- ✅ Right to be informed (audit logs)
- ✅ Data protection by design
- ⚠️ Right to erasure (implementation stub)

## Audit Logging

All sensitive operations are logged:
- User login/logout events
- Patient record access
- Prediction requests
- Data exports
- Administrative actions

### Audit Log Fields
| Field | Description |
|-------|-------------|
| timestamp | ISO 8601 timestamp |
| user_id | ID of the user performing the action |
| action | Type of action (read, create, update, delete) |
| resource_type | Type of resource accessed |
| resource_id | ID of the specific resource |
| ip_address | Client IP address |
| details | Additional context (JSON) |

## Recommendations for Production

1. **Use a dedicated KMS** for encryption key management
2. **Enable TLS/SSL** on all network connections
3. **Implement data retention policies**
4. **Regular security audits** and penetration testing
5. **Staff training** on data handling procedures
6. **Incident response plan** for data breaches
7. **Business Associate Agreements** with third-party providers
