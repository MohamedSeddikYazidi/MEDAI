# MedAI — AI Agents Documentation

## Agent System Overview

MedAI implements a **multi-agent architecture** where 7 specialized agents collaborate under a Supervisor to provide comprehensive medical decision support.

## Agent Descriptions

### 1. Patient Intake Agent (`patient_intake_agent.py`)

**Role:** Processes raw patient descriptions and extracts structured medical entities.

**Capabilities:**
- Medical Named Entity Recognition (NER) using regex patterns + LLM
- Symptom extraction and classification
- Medication recognition (23+ diabetes medications)
- Condition detection (diabetes, hypertension, heart failure, etc.)
- Urgency assessment (low / medium / high / critical)

**Input:** `{"symptoms": "free text description", "patient_info": {}}`

**Output:** Structured data with extracted symptoms, medications, conditions, urgency level, and recommended tests.

---

### 2. Diagnostic Agent (`diagnostic_agent.py`)

**Role:** Generates differential diagnoses with confidence scores.

**Pipeline:**
1. Receives structured patient data from Intake Agent
2. Queries RAG vector store for relevant medical knowledge
3. Sends patient context + retrieved knowledge to LLM
4. LLM generates ranked differential diagnoses
5. Each diagnosis includes ICD-10 code, confidence score, and reasoning

**Output:** Ranked list of diagnoses with confidence scores, clinical reasoning, recommended tests, and red flags.

---

### 3. Risk Prediction Agent (`risk_prediction_agent.py`)

**Role:** Predicts medical risks using trained ML models.

**Models:** XGBoost, Random Forest, LightGBM, Logistic Regression

**Features Used:** 26 engineered features from patient encounters

**Output:** 
- Binary prediction (readmitted within 30 days: yes/no)
- Probability score (0-1)
- Risk level (LOW / MEDIUM / HIGH)
- Top contributing factors with SHAP values
- Human-readable clinical summary via LLM

---

### 4. Medical Knowledge RAG Agent (`rag_agent.py`)

**Role:** Searches the medical knowledge base for evidence-based answers.

**Knowledge Base Includes:**
- ADA Diabetes Management Guidelines 2024
- Diabetes Medication Reference
- Hospital Readmission Risk Factors
- ICD-10 Diabetes Code Reference
- Clinical Decision Support - Diabetes Emergencies

**Pipeline:**
1. Query → ChromaDB vector search (cosine similarity)
2. Top-K relevant chunks retrieved
3. LLM generates contextualized answer with source citations
4. Returns relevance scores for each source

---

### 5. Treatment Recommendation Agent (`treatment_agent.py`)

**Role:** Generates evidence-based treatment plans.

**Output includes:**
- Prioritized treatment plan with evidence levels (A/B/C)
- Medication recommendations with dosing
- Lifestyle modifications
- Monitoring plan (tests + frequency)
- Safety alerts and drug interaction warnings
- Follow-up schedule
- Specialist referrals

---

### 6. BI & Analytics Agent (`bi_agent.py`)

**Role:** Transforms the diabetic dataset into actionable insights.

**Dashboard Types:**
1. **Executive** — KPIs, readmission rates, demographics
2. **Predictive** — Risk distribution, trends by age/admission type
3. **Clinical** — A1C results, medication patterns, specialty workload
4. **Operational** — Hospital stay distribution, alerts, priority cases

---

### 7. Supervisor Agent (`supervisor_agent.py`)

**Role:** Orchestrates all agents and manages workflows.

**Query Routing:**
- Automatically classifies incoming queries
- Routes to appropriate agent(s)
- Manages the full analysis pipeline
- Aggregates responses from multiple agents
- Calculates overall confidence scores

**Full Analysis Pipeline:**
Patient Intake → Diagnostic → Risk Prediction → Treatment Recommendation
