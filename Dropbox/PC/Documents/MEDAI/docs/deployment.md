# MedAI — Deployment Guide

## Local Development

### Prerequisites
- Python 3.11+ 
- Node.js 18+
- (Optional) OpenAI API key

### Backend Setup
```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Initialize database and seed users
python -c "from backend.database.init_db import init_database; init_database()"

# Ingest medical knowledge into RAG
python -m rag.ingestion

# Train ML models
python -m models.training

# Start backend server
uvicorn backend.main:app --reload --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Access
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## Docker Deployment

### Quick Start
```bash
cd docker
docker-compose up -d
```

### Services
| Service | Port | Description |
|---------|------|-------------|
| backend | 8000 | FastAPI server |
| frontend | 3000 | Next.js app |
| postgres | 5432 | Database |
| redis | 6379 | Cache |
| chromadb | 8001 | Vector database |

### Environment Variables
Set in `.env` file or docker-compose environment:
- `OPENAI_API_KEY` — For LLM features
- `LLM_PROVIDER` — "openai" or "ollama"
- `DATABASE_URL` — PostgreSQL connection string

---

## Production Considerations

### Security
1. Change all secret keys in `.env`
2. Use PostgreSQL instead of SQLite
3. Enable HTTPS via reverse proxy (nginx)
4. Restrict CORS origins
5. Enable rate limiting
6. Set `DEBUG=false`

### Scaling
- Backend: Run multiple uvicorn workers with gunicorn
- Frontend: Build static with `npm run build`
- Database: Use PostgreSQL with connection pooling
- Cache: Use Redis cluster
- ML Models: Pre-load into memory on startup

### Monitoring (Bonus)
Add Prometheus + Grafana for production monitoring:
```yaml
# Add to docker-compose.yml
prometheus:
  image: prom/prometheus
  ports: ["9090:9090"]

grafana:
  image: grafana/grafana
  ports: ["3001:3000"]
```
