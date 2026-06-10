"""
Authentication for LexiScan — JWT (PyJWT) + bcrypt password hashing.

Provides:
  - users table bootstrap
  - register / authenticate helpers
  - JWT issue + verify
  - a FastAPI dependency `get_current_user` that guards protected routes
"""

import os
import sqlite3
import datetime as dt

import jwt
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# In production set LEXISCAN_SECRET as an env var. The fallback keeps the demo
# runnable out of the box.
SECRET_KEY = os.environ.get("LEXISCAN_SECRET", "lexiscan-dev-secret-change-me")
ALGORITHM = "HS256"
TOKEN_TTL_HOURS = 24

DB_PATH = os.environ.get("LEXISCAN_DB", "lexiscan.db")

_bearer = HTTPBearer(auto_error=False)


def _db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_auth_db():
    conn = _db()
    conn.execute(
        """CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT,
            email         TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at    TEXT
        )"""
    )
    conn.commit()
    conn.close()


# ── Password hashing ─────────────────────────────────────────────────────────
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except (ValueError, TypeError):
        return False


# ── User management ──────────────────────────────────────────────────────────
def create_user(name: str, email: str, password: str) -> dict:
    email = email.strip().lower()
    conn = _db()
    existing = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
    if existing:
        conn.close()
        raise HTTPException(status_code=409, detail="An account with this email already exists.")

    cursor = conn.execute(
        "INSERT INTO users (name, email, password_hash, created_at) VALUES (?,?,?,?)",
        (name.strip() or email.split("@")[0], email, hash_password(password), dt.datetime.utcnow().isoformat()),
    )
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return {"id": user_id, "name": name.strip() or email.split("@")[0], "email": email}


def authenticate_user(email: str, password: str) -> dict:
    email = email.strip().lower()
    conn = _db()
    row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    if not row or not verify_password(password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    return {"id": row["id"], "name": row["name"], "email": row["email"]}


# ── JWT ──────────────────────────────────────────────────────────────────────
def create_access_token(user: dict) -> str:
    payload = {
        "sub": str(user["id"]),
        "email": user["email"],
        "name": user["name"],
        "exp": dt.datetime.utcnow() + dt.timedelta(hours=TOKEN_TTL_HOURS),
        "iat": dt.datetime.utcnow(),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(creds: HTTPAuthorizationCredentials = Depends(_bearer)) -> dict:
    if creds is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = jwt.decode(creds.credentials, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Session expired — please log in again.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid authentication token.")

    return {
        "id": int(payload["sub"]),
        "email": payload.get("email"),
        "name": payload.get("name"),
    }
