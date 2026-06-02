# Architecture Design Document: LexiScan Auto

## 1. System Overview
LexiScan Auto is a real-time, full-stack Artificial Intelligence microservice designed to ingest legal PDF documents, intelligently extract key structured data (Named Entity Recognition), and redact Personally Identifiable Information (PII) before returning the results to a beautiful frontend dashboard.

## 2. Technology Stack
*   **Frontend**: React.js, Vite, Vanilla CSS (Glassmorphism UI)
*   **Backend API**: FastAPI, Python 3, Uvicorn
*   **NLP & ML Core**: Spacy (en_core_web_sm), PyMuPDF (fitz)
*   **Database**: SQLite

## 3. Data Flow
1. **Client Request**: The React frontend sends a `multipart/form-data` request containing the PDF to the FastAPI backend.
2. **Text Extraction**: The `PyMuPDF` engine strips raw text from the PDF at high speed without relying on clunky system dependencies like Tesseract.
3. **Named Entity Recognition (NER)**: The text is passed into the `Spacy` NLP pipeline. The model identifies Dates, People, Organizations, and Financial amounts.
4. **Validation Engine**: Regex rules are applied to format currencies and detect complex strings like "Termination Clauses".
5. **PII Redaction**: A privacy layer masks the extracted sensitive names and financial amounts in the original text.
6. **Data Persistence**: The structured entities are serialized into JSON and saved to the `SQLite` database to enable future searching/indexing.
7. **Client Response**: The backend returns a JSON payload containing the structured data, confidence flags, and redacted text to the React dashboard.

## 4. Scalability Considerations
While currently running locally, the FastAPI and NLP modules are entirely stateless. In a production environment, this application can be containerized using Docker and scaled horizontally using Kubernetes. The SQLite database should be replaced with PostgreSQL or Elasticsearch for distributed text search.
