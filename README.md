# LexiScan Auto v3 — AI Contract Intelligence Platform

A full-stack AI application that reads legal contract PDFs and turns them into structured
intelligence — named entities, a **machine-learning–predicted contract type**, confidence &
risk scores, and a PII-redacted copy — behind a **secure, authenticated** dashboard with a
public landing page. Everything runs **fully on-device — no external AI API, no API keys.**

## Project Structure
- `ai/` — NLP pipeline (Spacy + PyMuPDF), the **offline ML contract-type classifier**, and a mock PDF generator
- `backend/` — FastAPI server with **JWT auth**, per-user CRUD API and SQLite
- `frontend/` — React (Vite) SPA: **landing page**, login/signup, multi-tab glassmorphism dashboard
- `generate_report.py` — produces **`WEEKLY_REPORT.pdf`**, the weekly intern progress report

## Features
- **🏠 Landing page** — hero, feature grid, how-it-works and call-to-action for logged-out visitors
- **🔐 Authentication** — JWT (PyJWT) login/signup with bcrypt-hashed passwords; contracts are **private per user**
- **🤖 AI contract-type prediction** — an offline scikit-learn model (TF-IDF + Logistic Regression) classifies each
  contract as **NDA / Employment / Lease / Service / Sales / Loan**, with a ranked probability chart
- **🔍 Named Entity Recognition** — Parties, Amounts, Dates, Locations, Termination Clauses (Spacy)
- **🛡️ PII Redaction** — color-coded `[PARTY_REDACTED]` / `[AMOUNT_REDACTED]` masking
- **📊 Confidence scoring** (0–100%) and **risk assessment** (LOW / MEDIUM / HIGH) with review flags
- **🗂 Document History** — per-user table with predicted type, confidence, risk and delete
- **📈 Analytics Dashboard** — stats overview, risk distribution **and predicted-type breakdown**
- **⬇ Export** redacted text · **🔔 Toast** notifications · animated processing pipeline

## 🚀 Running the App

Open two terminals in `Zaalima Intern Project 3/`.

### Terminal 1 — Backend
```bash
pip install -r backend/requirements.txt
python -m spacy download en_core_web_sm   # first run only
python -m uvicorn backend.main:app --reload --port 8000
```
> Optional: set `LEXISCAN_SECRET` (JWT signing key) and `LEXISCAN_DB` (database path) as
> environment variables. Sensible defaults are used out of the box.

### Terminal 2 — Frontend
```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`, click **Get Started**, create an account, and upload a PDF.

### Generate a test PDF
```bash
python ai/generate_mock_pdf.py
```
Then drag `sample_contract.pdf` into the dashboard.

### Generate the weekly project report
```bash
python generate_report.py        # writes WEEKLY_REPORT.pdf
```

## API Endpoints

All `/contracts*`, `/extract` and `/stats` routes require a **`Authorization: Bearer <token>`** header.

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST   | `/api/v1/auth/register`     | —   | Create an account, returns a JWT |
| POST   | `/api/v1/auth/login`        | —   | Log in, returns a JWT |
| GET    | `/api/v1/auth/me`           | ✓   | Current user from token |
| POST   | `/api/v1/extract`           | ✓   | Analyze a PDF (NER + ML prediction + redaction) |
| GET    | `/api/v1/contracts`         | ✓   | List the user's contracts |
| GET    | `/api/v1/contracts/{id}`    | ✓   | Get a single contract |
| DELETE | `/api/v1/contracts/{id}`    | ✓   | Delete a contract |
| GET    | `/api/v1/stats`             | ✓   | Aggregated analytics incl. type breakdown |

## Tech Stack
FastAPI · Uvicorn · SQLite · Spacy NER · PyMuPDF · **scikit-learn (TF-IDF + LogisticRegression)** ·
**PyJWT** · **bcrypt** · React 19 · Vite · **reportlab**
