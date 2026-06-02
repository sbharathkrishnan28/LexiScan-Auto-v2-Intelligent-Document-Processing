import fitz
import spacy
import re
import os
import time

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    os.system("python -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")


def _calculate_confidence(entities, word_count):
    score = 0
    if entities["parties"]:
        score += 30
    if entities["amounts"]:
        score += 30
    if entities["dates"]:
        score += 20
    if entities["termination_clauses"]:
        score += 10
    if word_count > 50:
        score += 10
    return min(score, 100)


def _assess_risk(entities, confidence):
    if confidence < 40 or len(entities["parties"]) == 0:
        return "HIGH"
    if confidence < 70 or len(entities["amounts"]) == 0:
        return "MEDIUM"
    return "LOW"


def process_pdf(pdf_bytes: bytes) -> dict:
    start_time = time.time()

    # 1. Fast text extraction via PyMuPDF
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    raw_text = ""
    page_count = len(doc)
    for page in doc:
        raw_text += page.get_text() + "\n"

    word_count = len(raw_text.split())
    sentence_count = len([s for s in raw_text.split(".") if s.strip()])

    # 2. NER via Spacy
    spacy_doc = nlp(raw_text)

    extracted_data = {
        "dates": [],
        "parties": [],
        "amounts": [],
        "termination_clauses": [],
        "locations": [],
        "organizations": [],
        "persons": [],
    }

    for ent in spacy_doc.ents:
        if ent.label_ == "DATE" and ent.text not in extracted_data["dates"]:
            extracted_data["dates"].append(ent.text)
        elif ent.label_ == "ORG" and ent.text not in extracted_data["parties"]:
            extracted_data["parties"].append(ent.text)
            extracted_data["organizations"].append(ent.text)
        elif ent.label_ == "PERSON" and ent.text not in extracted_data["parties"]:
            extracted_data["parties"].append(ent.text)
            extracted_data["persons"].append(ent.text)
        elif ent.label_ == "MONEY" and ent.text not in extracted_data["amounts"]:
            extracted_data["amounts"].append(ent.text)
        elif ent.label_ in ["GPE", "LOC"] and ent.text not in extracted_data["locations"]:
            extracted_data["locations"].append(ent.text)

    # 3. Rule-based termination clause detection
    term_patterns = [
        r"(terminate|termination).{0,80}(days|notice|immediate|written)",
        r"(cancel|cancellation).{0,60}(days|notice|effect)",
        r"(breach).{0,60}(cure|period|notice)",
    ]
    for pat in term_patterns:
        for match in re.compile(pat, re.IGNORECASE).finditer(raw_text):
            clause = match.group(0).strip()
            if clause not in extracted_data["termination_clauses"]:
                extracted_data["termination_clauses"].append(clause)

    # 4. Clean financial amounts
    clean_amounts = []
    for amt in extracted_data["amounts"]:
        cleaned = re.sub(r"[^\d\.]", "", amt)
        if cleaned:
            try:
                clean_amounts.append(float(cleaned))
            except ValueError:
                pass

    # 5. Confidence scoring & risk level
    confidence_score = _calculate_confidence(extracted_data, word_count)
    risk_level = _assess_risk(extracted_data, confidence_score)

    requires_review = confidence_score < 50
    flags = []
    if not extracted_data["parties"]:
        flags.append("No parties identified — human review required.")
    if not clean_amounts:
        flags.append("No financial amounts detected — manual verification recommended.")
    if not extracted_data["dates"]:
        flags.append("No dates found — contract timeline unclear.")

    # 6. PII redaction
    redacted_text = raw_text
    for party in extracted_data["parties"]:
        redacted_text = redacted_text.replace(party, "[PARTY_REDACTED]")
    for amt in extracted_data["amounts"]:
        redacted_text = redacted_text.replace(amt, "[AMOUNT_REDACTED]")

    processing_time_ms = round((time.time() - start_time) * 1000)

    entity_count = (
        len(extracted_data["parties"])
        + len(extracted_data["amounts"])
        + len(extracted_data["dates"])
        + len(extracted_data["locations"])
    )

    return {
        "raw_text": raw_text,
        "redacted_text": redacted_text,
        "entities": extracted_data,
        "clean_amounts": clean_amounts,
        "human_review_required": requires_review,
        "flags": flags,
        "confidence_score": confidence_score,
        "risk_level": risk_level,
        "stats": {
            "word_count": word_count,
            "sentence_count": sentence_count,
            "page_count": page_count,
            "processing_time_ms": processing_time_ms,
            "entity_count": entity_count,
        },
    }
