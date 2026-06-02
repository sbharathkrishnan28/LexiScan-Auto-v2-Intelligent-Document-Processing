from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
import json
import sqlite3
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ai.pipeline import process_pdf

app = FastAPI(title="LexiScan API v2", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "lexiscan.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute(
        """CREATE TABLE IF NOT EXISTS contracts (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            filename            TEXT,
            parties             TEXT,
            amounts             TEXT,
            dates               TEXT,
            locations           TEXT,
            max_amount          REAL,
            word_count          INTEGER,
            page_count          INTEGER,
            confidence_score    INTEGER,
            risk_level          TEXT,
            review_required     BOOLEAN,
            redacted_text       TEXT,
            processing_time_ms  INTEGER,
            created_at          TEXT
        )"""
    )
    conn.commit()
    conn.close()


init_db()


@app.post("/api/v1/extract")
async def extract_contract_data(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    pdf_bytes = await file.read()
    result = process_pdf(pdf_bytes)

    max_amt = max(result["clean_amounts"]) if result["clean_amounts"] else 0.0

    conn = get_db()
    cursor = conn.execute(
        """INSERT INTO contracts
           (filename, parties, amounts, dates, locations, max_amount, word_count, page_count,
            confidence_score, risk_level, review_required, redacted_text, processing_time_ms, created_at)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            file.filename,
            json.dumps(result["entities"]["parties"]),
            json.dumps(result["entities"]["amounts"]),
            json.dumps(result["entities"]["dates"]),
            json.dumps(result["entities"]["locations"]),
            max_amt,
            result["stats"]["word_count"],
            result["stats"]["page_count"],
            result["confidence_score"],
            result["risk_level"],
            result["human_review_required"],
            result["redacted_text"],
            result["stats"]["processing_time_ms"],
            datetime.utcnow().isoformat(),
        ),
    )
    doc_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return {"status": "success", "id": doc_id, "filename": file.filename, "analysis": result}


@app.get("/api/v1/contracts")
async def list_contracts():
    conn = get_db()
    rows = conn.execute(
        """SELECT id, filename, parties, max_amount, confidence_score, risk_level,
                  review_required, word_count, page_count, processing_time_ms, created_at
           FROM contracts ORDER BY id DESC LIMIT 100"""
    ).fetchall()
    conn.close()

    contracts = [
        {
            "id": r["id"],
            "filename": r["filename"],
            "parties": json.loads(r["parties"]) if r["parties"] else [],
            "max_amount": r["max_amount"],
            "confidence_score": r["confidence_score"],
            "risk_level": r["risk_level"],
            "review_required": bool(r["review_required"]),
            "word_count": r["word_count"],
            "page_count": r["page_count"],
            "processing_time_ms": r["processing_time_ms"],
            "created_at": r["created_at"],
        }
        for r in rows
    ]
    return {"contracts": contracts, "total": len(contracts)}


@app.get("/api/v1/contracts/{contract_id}")
async def get_contract(contract_id: int):
    conn = get_db()
    row = conn.execute("SELECT * FROM contracts WHERE id = ?", (contract_id,)).fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Contract not found.")

    return {
        "id": row["id"],
        "filename": row["filename"],
        "parties": json.loads(row["parties"]) if row["parties"] else [],
        "amounts": json.loads(row["amounts"]) if row["amounts"] else [],
        "dates": json.loads(row["dates"]) if row["dates"] else [],
        "locations": json.loads(row["locations"]) if row["locations"] else [],
        "max_amount": row["max_amount"],
        "confidence_score": row["confidence_score"],
        "risk_level": row["risk_level"],
        "review_required": bool(row["review_required"]),
        "word_count": row["word_count"],
        "page_count": row["page_count"],
        "redacted_text": row["redacted_text"],
        "processing_time_ms": row["processing_time_ms"],
        "created_at": row["created_at"],
    }


@app.delete("/api/v1/contracts/{contract_id}")
async def delete_contract(contract_id: int):
    conn = get_db()
    result = conn.execute("DELETE FROM contracts WHERE id = ?", (contract_id,))
    if result.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Contract not found.")
    conn.commit()
    conn.close()
    return {"status": "deleted", "id": contract_id}


@app.get("/api/v1/stats")
async def get_stats():
    conn = get_db()
    row = conn.execute(
        """SELECT
            COUNT(*)                                          AS total,
            AVG(confidence_score)                            AS avg_confidence,
            SUM(review_required)                             AS needs_review,
            COUNT(CASE WHEN risk_level='HIGH'   THEN 1 END)  AS high_risk,
            COUNT(CASE WHEN risk_level='MEDIUM' THEN 1 END)  AS medium_risk,
            COUNT(CASE WHEN risk_level='LOW'    THEN 1 END)  AS low_risk,
            AVG(processing_time_ms)                          AS avg_ms,
            AVG(word_count)                                  AS avg_words
           FROM contracts"""
    ).fetchone()
    conn.close()

    return {
        "total_contracts": row["total"],
        "avg_confidence": round(row["avg_confidence"] or 0, 1),
        "needs_review": row["needs_review"] or 0,
        "avg_processing_ms": round(row["avg_ms"] or 0),
        "avg_word_count": round(row["avg_words"] or 0),
        "risk_breakdown": {
            "high": row["high_risk"] or 0,
            "medium": row["medium_risk"] or 0,
            "low": row["low_risk"] or 0,
        },
    }
