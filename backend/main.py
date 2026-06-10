from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
import sys
import os
import json
import sqlite3
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ai.pipeline import process_pdf
from backend.auth import (
    init_auth_db,
    create_user,
    authenticate_user,
    create_access_token,
    get_current_user,
)

app = FastAPI(title="LexiScan API v3", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = os.environ.get("LEXISCAN_DB", "lexiscan.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute(
        """CREATE TABLE IF NOT EXISTS contracts (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id             INTEGER,
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
            predicted_type      TEXT,
            predicted_label     TEXT,
            predicted_proba     INTEGER,
            created_at          TEXT
        )"""
    )
    # Migrate older DBs that predate the new columns.
    existing = {r["name"] for r in conn.execute("PRAGMA table_info(contracts)").fetchall()}
    for col, decl in [
        ("user_id", "INTEGER"),
        ("predicted_type", "TEXT"),
        ("predicted_label", "TEXT"),
        ("predicted_proba", "INTEGER"),
    ]:
        if col not in existing:
            conn.execute(f"ALTER TABLE contracts ADD COLUMN {col} {decl}")
    conn.commit()
    conn.close()


init_db()
init_auth_db()


# ─── Auth schemas ────────────────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    name: str = ""
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


def _auth_response(user: dict) -> dict:
    token = create_access_token(user)
    return {"access_token": token, "token_type": "bearer", "user": user}


@app.post("/api/v1/auth/register")
async def register(body: RegisterRequest):
    if len(body.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")
    user = create_user(body.name, body.email, body.password)
    return _auth_response(user)


@app.post("/api/v1/auth/login")
async def login(body: LoginRequest):
    user = authenticate_user(body.email, body.password)
    return _auth_response(user)


@app.get("/api/v1/auth/me")
async def me(user: dict = Depends(get_current_user)):
    return {"user": user}


# ─── Contract endpoints (all scoped to the authenticated user) ───────────────
@app.post("/api/v1/extract")
async def extract_contract_data(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user),
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    pdf_bytes = await file.read()
    result = process_pdf(pdf_bytes)

    max_amt = max(result["clean_amounts"]) if result["clean_amounts"] else 0.0
    pred = result.get("prediction", {})

    conn = get_db()
    cursor = conn.execute(
        """INSERT INTO contracts
           (user_id, filename, parties, amounts, dates, locations, max_amount, word_count, page_count,
            confidence_score, risk_level, review_required, redacted_text, processing_time_ms,
            predicted_type, predicted_label, predicted_proba, created_at)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            user["id"],
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
            pred.get("category"),
            pred.get("category_label"),
            pred.get("confidence"),
            datetime.utcnow().isoformat(),
        ),
    )
    doc_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return {"status": "success", "id": doc_id, "filename": file.filename, "analysis": result}


@app.get("/api/v1/contracts")
async def list_contracts(user: dict = Depends(get_current_user)):
    conn = get_db()
    rows = conn.execute(
        """SELECT id, filename, parties, max_amount, confidence_score, risk_level,
                  review_required, word_count, page_count, processing_time_ms,
                  predicted_type, predicted_label, predicted_proba, created_at
           FROM contracts WHERE user_id = ? ORDER BY id DESC LIMIT 100""",
        (user["id"],),
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
            "predicted_type": r["predicted_type"],
            "predicted_label": r["predicted_label"],
            "predicted_proba": r["predicted_proba"],
            "created_at": r["created_at"],
        }
        for r in rows
    ]
    return {"contracts": contracts, "total": len(contracts)}


@app.get("/api/v1/contracts/{contract_id}")
async def get_contract(contract_id: int, user: dict = Depends(get_current_user)):
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM contracts WHERE id = ? AND user_id = ?", (contract_id, user["id"])
    ).fetchone()
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
        "predicted_type": row["predicted_type"],
        "predicted_label": row["predicted_label"],
        "predicted_proba": row["predicted_proba"],
        "created_at": row["created_at"],
    }


@app.delete("/api/v1/contracts/{contract_id}")
async def delete_contract(contract_id: int, user: dict = Depends(get_current_user)):
    conn = get_db()
    result = conn.execute(
        "DELETE FROM contracts WHERE id = ? AND user_id = ?", (contract_id, user["id"])
    )
    if result.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Contract not found.")
    conn.commit()
    conn.close()
    return {"status": "deleted", "id": contract_id}


@app.get("/api/v1/stats")
async def get_stats(user: dict = Depends(get_current_user)):
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
           FROM contracts WHERE user_id = ?""",
        (user["id"],),
    ).fetchone()

    type_rows = conn.execute(
        """SELECT predicted_type AS t, COUNT(*) AS c
           FROM contracts WHERE user_id = ? AND predicted_type IS NOT NULL
           GROUP BY predicted_type ORDER BY c DESC""",
        (user["id"],),
    ).fetchall()
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
        "type_breakdown": [{"type": r["t"], "count": r["c"]} for r in type_rows],
    }
