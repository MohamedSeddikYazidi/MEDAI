# MedAI — System Architecture Documentation

## 1. Architecture Overview

MedAI follows a **distributed modular architecture** with clear separation of concerns:

- **Presentation Layer** → Next.js + TailwindCSS
- **API Layer** → FastAPI with REST + WebSocket
- **Agent Layer** → 7 specialized AI agents orchestrated by a Supervisor
- **Data Layer** → SQLite/PostgreSQL + ChromaDB + Redis
- **ML Layer** → Scikit-learn, XGBoost, LightGBM, SHAP

## 2. Agent Communication Flow

```
User Request
    │
    ▼
┌─────────────────┐
│  Supervisor      │  ← Routes queries to appropriate agents
│  Agent           │
└────────┬────────┘
         │
    ┌────┼────┬────────┬────────┬────────┐
    ▼    ▼    ▼        ▼        ▼        ▼
┌──────┐┌──────┐┌──────────┐┌──────┐┌──────┐┌──────┐
│Intake││Diag- ││Risk      ││ RAG  ││Treat-││  BI  │
│Agent ││nostic││Prediction││Agent ││ment  ││Agent │
└──────┘└──────┘└──────────┘└──────┘└──────┘└──────┘
    │       │        │          │       │       │
    ▼       ▼        ▼          ▼       ▼       ▼
┌──────┐┌──────┐┌──────────┐┌──────┐
│  NLP ││ RAG  ││ML Models ││Vector│
│Engine││Search││+ SHAP    ││Store │
└──────┘└──────┘└──────────┘└──────┘
```

## 3. Data Flow

### Patient Analysis Pipeline
1. User submits symptoms via Chat or Analysis panel
2. Supervisor Agent classifies query type
3. Patient Intake Agent extracts medical entities (NER)
4. Diagnostic Agent queries RAG + uses LLM for differential diagnosis
5. Risk Prediction Agent runs ML model + SHAP explanation
6. Treatment Agent generates evidence-based recommendations
7. Supervisor aggregates all results and returns to user

### BI Analytics Pipeline
1. ETL pipeline loads diabetic_data.csv → Database
2. Feature engineering creates ML-ready features
3. BI Agent queries database for aggregations
4. Dashboard components render charts via Recharts

## 4. Database Schema

### Core Tables
- `users` — Authentication and RBAC
- `patients` — Patient demographics
- `encounters` — Hospital visit records
- `predictions` — ML prediction results with SHAP
- `diagnosis_results` — Agent diagnostic outputs
- `chat_sessions` — Chat session management
- `chat_messages` — Individual messages
- `audit_logs` — Compliance audit trail
- `medical_documents` — RAG document tracking

## 5. Security Architecture

### Authentication Flow
```
Client → Login (username/password)
       → Server validates → Issues JWT (access + refresh)
       → Client stores tokens
       → Subsequent requests include Bearer token
       → Server validates JWT on each request
       → RBAC checks user role against endpoint permissions
```

### Data Protection
- AES-256 encryption for PII fields
- PII anonymization utilities
- HIPAA/GDPR compliance simulation
- Complete audit trail

## 6. Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | Next.js 15, TailwindCSS, Recharts, Framer Motion | UI/UX |
| Backend | FastAPI, SQLAlchemy, Pydantic | API Server |
| AI/ML | XGBoost, LightGBM, Scikit-learn, SHAP | Prediction |
| NLP | spaCy, regex patterns, LLM | Entity Extraction |
| RAG | ChromaDB, sentence-transformers | Knowledge Retrieval |
| LLM | OpenAI API / Ollama | Generation |
| Database | SQLite / PostgreSQL | Structured Data |
| Vector DB | ChromaDB | Embeddings |
| Cache | Redis | Performance |
| Deploy | Docker, Docker Compose | Containerization |
