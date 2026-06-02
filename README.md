# LexiScan Auto v2 — Intelligent Document Processing

A full-stack AI application that extracts and redacts sensitive legal entities from PDFs in real-time, featuring a premium glassmorphism dashboard with analytics.

## Project Structure
- `ai/` — NLP pipeline (Spacy + PyMuPDF) and mock PDF generator
- `backend/` — FastAPI server with full CRUD API and SQLite indexing
- `frontend/` — React (Vite) SPA with multi-tab glassmorphism dashboard

## Features
- **Drag-and-drop upload** with visual feedback
- **Named Entity Recognition** — Parties, Amounts, Dates, Locations, Termination Clauses
- **PII Redaction** — color-coded `[PARTY_REDACTED]` / `[AMOUNT_REDACTED]` tags
- **Confidence scoring** (0–100%) with animated progress bar
- **Risk assessment** — LOW / MEDIUM / HIGH badge
- **Processing steps** animation during analysis
- **Document History** tab — sortable table with delete
- **Analytics Dashboard** — stats overview + risk distribution chart
- **Export** — download redacted text as `.txt`
- **Toast notifications** for all actions

## 🚀 Running the App

Open two terminals in `Zaalima Intern Project 3/`.

### Terminal 1 — Backend
```bash
pip install -r backend/requirements.txt
python -m uvicorn backend.main:app --reload --port 8000
```

### Terminal 2 — Frontend
```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` in your browser.

### Generate a test PDF
```bash
python ai/generate_mock_pdf.py
```
Then drag `sample_contract.pdf` into the dashboard.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST   | `/api/v1/extract`           | Analyze a PDF |
| GET    | `/api/v1/contracts`         | List all indexed contracts |
| GET    | `/api/v1/contracts/{id}`    | Get a single contract |
| DELETE | `/api/v1/contracts/{id}`    | Delete a contract |
| GET    | `/api/v1/stats`             | Aggregated analytics |
