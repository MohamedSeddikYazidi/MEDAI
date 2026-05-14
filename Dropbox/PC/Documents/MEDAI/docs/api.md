# MedAI — API Reference

## Base URL
```
http://localhost:8000
```

## Authentication

All protected endpoints require a Bearer token in the Authorization header:
```
Authorization: Bearer <access_token>
```

### POST `/api/auth/login`
Login and receive JWT tokens.

**Body** (form-urlencoded):
| Field | Type | Required |
|-------|------|----------|
| username | string | Yes |
| password | string | Yes |

**Response:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "username": "admin",
    "email": "admin@medai.com",
    "full_name": "System Administrator",
    "role": "admin"
  }
}
```

### POST `/api/auth/refresh`
Refresh an expired access token.

### GET `/api/auth/me`
Get current user profile. 🔒 Requires authentication.

---

## AI Agents

### POST `/api/agents/analyze` 🔒
Run the full multi-agent analysis pipeline.

**Body:**
```json
{
  "query": "Patient presents with fatigue, blurred vision, and frequent urination",
  "query_type": "full_analysis",
  "patient_info": {"age": "[60-70)", "gender": "Male"}
}
```

### POST `/api/agents/intake` 🔒
Process patient intake with NLP extraction.

### POST `/api/agents/diagnose` 🔒
Get differential diagnoses.

### POST `/api/agents/predict-risk` 🔒
Predict readmission risk with SHAP explanation.

**Body:**
```json
{
  "features": {
    "age_numeric": 65,
    "time_in_hospital": 5,
    "num_medications": 15,
    "number_inpatient": 2,
    "number_emergency": 1
  }
}
```

### POST `/api/agents/search-knowledge` 🔒
Search the medical knowledge base (RAG).

### POST `/api/agents/recommend-treatment` 🔒
Get evidence-based treatment recommendations.

---

## Analytics

### GET `/api/analytics/kpis` 🔒
Get executive KPIs.

### GET `/api/analytics/dashboard/{type}` 🔒
Get dashboard data. Types: `executive_dashboard`, `predictive_dashboard`, `clinical_dashboard`, `operational_dashboard`.

### GET `/api/analytics/model-metrics` 🔒
Get ML model performance metrics.

---

## Chat

### POST `/api/chat` 🔒
Send a message to the medical AI chat.

### WebSocket `/api/chat/ws`
Real-time chat via WebSocket.

---

## Patients

### GET `/api/patients` 🔒
List patients with pagination.

### GET `/api/patients/{id}` 🔒
Get patient details with encounters.

### GET `/api/patients/stats/summary` 🔒
Get aggregate patient statistics.

---

## System

### GET `/api/health`
Health check (no auth required).

### GET `/api/system/info` 🔒
Get system info (loaded models, RAG status, agents).

---

## Interactive Docs

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
