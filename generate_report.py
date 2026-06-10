"""
Weekly Project Report generator for LexiScan Auto.

Produces WEEKLY_REPORT.pdf — a polished, multi-page intern progress report
documenting the work completed each week, the architecture, the tech stack and
the deliverables.

Usage:
    python generate_report.py
"""

from datetime import date

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, ListFlowable, ListItem, PageBreak,
)

OUTPUT = "WEEKLY_REPORT.pdf"

# Brand palette (matches the app)
INDIGO = colors.HexColor("#6366f1")
PURPLE = colors.HexColor("#a855f7")
DARK = colors.HexColor("#0f172a")
SLATE = colors.HexColor("#475569")
LIGHT_BG = colors.HexColor("#f1f5ff")
GREEN = colors.HexColor("#16a34a")


# ── Weekly content ───────────────────────────────────────────────────────────
WEEKS = [
    {
        "title": "Week 1 — Foundation & AI Pipeline",
        "goal": "Stand up the backend and the core NLP extraction engine.",
        "tasks": [
            "Initialised the project structure (ai / backend / frontend) and Git repository.",
            "Built the FastAPI backend with CORS and a SQLite persistence layer.",
            "Implemented the PDF text-extraction pipeline using PyMuPDF (no OCR).",
            "Integrated Spacy Named Entity Recognition to extract parties, dates, amounts and locations.",
            "Added rule-based termination-clause detection with regex patterns.",
            "Created the POST /extract endpoint and a sample contract for testing.",
        ],
        "deliverable": "Working API that turns a PDF into structured entities.",
    },
    {
        "title": "Week 2 — Dashboard, Scoring & PII Redaction",
        "goal": "Build the React dashboard and add intelligence on top of raw entities.",
        "tasks": [
            "Built the React + Vite single-page dashboard with a glassmorphism design system.",
            "Implemented drag-and-drop PDF upload with an animated processing pipeline.",
            "Added a 0–100 AI confidence score and LOW / MEDIUM / HIGH risk assessment.",
            "Built the PII-redaction engine that masks party names and financial figures.",
            "Added multi-tab navigation: Upload, Results, History and Stats.",
            "Implemented full CRUD (list / detail / delete) and an analytics dashboard.",
        ],
        "deliverable": "End-to-end app: upload a contract, see scored, redacted results.",
    },
    {
        "title": "Week 3 — ML Prediction, Authentication & Landing Page",
        "goal": "Add a machine-learning model, secure the app, and ship a public landing page.",
        "tasks": [
            "Built an offline contract-type classifier (TF-IDF + Logistic Regression, scikit-learn) "
            "predicting NDA / Employment / Lease / Service / Sales / Loan — no external API.",
            "Wired the prediction into the pipeline, results view, history table and stats.",
            "Added JWT authentication (PyJWT) with bcrypt-hashed passwords and a users table.",
            "Scoped all contracts to the authenticated user; protected every data endpoint.",
            "Built register / login screens and token-based session handling on the frontend.",
            "Designed and built a marketing landing page (hero, features, how-it-works, CTA).",
            "Added this automated weekly-report PDF generator (reportlab).",
        ],
        "deliverable": "Secure, multi-user product with ML prediction and a public landing page.",
    },
]

TECH_STACK = [
    ("Backend", "FastAPI · Uvicorn · SQLite · Pydantic"),
    ("AI / NLP", "Spacy NER · PyMuPDF · scikit-learn (TF-IDF + LogisticRegression)"),
    ("Auth", "PyJWT (JWT) · bcrypt password hashing"),
    ("Frontend", "React 19 · Vite · custom glassmorphism CSS"),
    ("Reporting", "reportlab (this PDF)"),
]

FEATURES = [
    ("NER Extraction", "Parties, dates, amounts, locations, termination clauses"),
    ("ML Type Prediction", "Offline classifier across 6 contract categories"),
    ("PII Redaction", "Automatic masking of names & financial figures"),
    ("Confidence & Risk", "0–100 score with LOW/MEDIUM/HIGH and review flags"),
    ("Authentication", "JWT + bcrypt; per-user private history"),
    ("Analytics", "Risk distribution, type breakdown, processing metrics"),
]


def build_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle("CoverTitle", fontName="Helvetica-Bold", fontSize=30,
                              textColor=INDIGO, alignment=TA_CENTER, leading=34, spaceAfter=6))
    styles.add(ParagraphStyle("CoverSub", fontName="Helvetica", fontSize=13,
                              textColor=SLATE, alignment=TA_CENTER, leading=18))
    styles.add(ParagraphStyle("H2", fontName="Helvetica-Bold", fontSize=15,
                              textColor=DARK, spaceBefore=14, spaceAfter=6, leading=18))
    styles.add(ParagraphStyle("WeekTitle", fontName="Helvetica-Bold", fontSize=14,
                              textColor=colors.white, leading=17))
    styles.add(ParagraphStyle("Goal", fontName="Helvetica-Oblique", fontSize=10.5,
                              textColor=SLATE, spaceAfter=4, leading=14))
    styles.add(ParagraphStyle("BodyText2", fontName="Helvetica", fontSize=10,
                              textColor=DARK, leading=15))
    styles.add(ParagraphStyle("Bullet2", fontName="Helvetica", fontSize=10,
                              textColor=DARK, leading=14))
    styles.add(ParagraphStyle("Deliver", fontName="Helvetica-Bold", fontSize=10,
                              textColor=GREEN, leading=14, spaceBefore=4))
    return styles


def section_rule():
    return HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e2e8f0"),
                      spaceBefore=8, spaceAfter=8)


def build():
    styles = build_styles()
    doc = SimpleDocTemplate(
        OUTPUT, pagesize=A4,
        leftMargin=20 * mm, rightMargin=20 * mm,
        topMargin=18 * mm, bottomMargin=18 * mm,
        title="LexiScan Auto — Weekly Project Report",
        author="Zaalima Intern",
    )
    story = []

    # ── Cover ────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 60 * mm))
    story.append(Paragraph("LexiScan Auto", styles["CoverTitle"]))
    story.append(Paragraph("AI Contract Intelligence Platform", styles["CoverSub"]))
    story.append(Spacer(1, 6 * mm))
    story.append(HRFlowable(width="40%", thickness=2, color=PURPLE,
                            spaceBefore=4, spaceAfter=10, hAlign="CENTER"))
    story.append(Paragraph("Weekly Project Progress Report", styles["CoverSub"]))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph(f"Zaalima Internship · Generated {date.today().strftime('%d %B %Y')}",
                          styles["CoverSub"]))
    story.append(Spacer(1, 40 * mm))

    summary = (
        "This report documents the weekly progress on <b>LexiScan Auto</b>, a full-stack AI "
        "application that reads legal contract PDFs and extracts structured intelligence — "
        "named entities, a machine-learning–predicted contract type, confidence and risk scores, "
        "and a PII-redacted copy of the document — behind a secure, authenticated dashboard."
    )
    story.append(Paragraph(summary, styles["BodyText2"]))
    story.append(PageBreak())

    # ── Overview: stack + features ───────────────────────────────────────────
    story.append(Paragraph("Project Overview", styles["H2"]))
    story.append(section_rule())

    story.append(Paragraph("Technology Stack", styles["H2"]))
    stack_rows = [[Paragraph(f"<b>{k}</b>", styles["BodyText2"]), Paragraph(v, styles["BodyText2"])]
                  for k, v in TECH_STACK]
    stack_tbl = Table(stack_rows, colWidths=[35 * mm, 130 * mm])
    stack_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), LIGHT_BG),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(stack_tbl)
    story.append(Spacer(1, 8))

    story.append(Paragraph("Key Features Delivered", styles["H2"]))
    feat_rows = [[Paragraph(f"<b>{k}</b>", styles["BodyText2"]), Paragraph(v, styles["BodyText2"])]
                 for k, v in FEATURES]
    feat_tbl = Table(feat_rows, colWidths=[45 * mm, 120 * mm])
    feat_tbl.setStyle(TableStyle([
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, LIGHT_BG]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(feat_tbl)
    story.append(PageBreak())

    # ── Weekly breakdown ─────────────────────────────────────────────────────
    story.append(Paragraph("Weekly Breakdown", styles["H2"]))
    story.append(section_rule())

    for wk in WEEKS:
        header = Table([[Paragraph(wk["title"], styles["WeekTitle"])]], colWidths=[165 * mm])
        header.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), INDIGO),
            ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("ROUNDEDCORNERS", [4, 4, 4, 4]),
        ]))
        story.append(header)
        story.append(Spacer(1, 4))
        story.append(Paragraph(f"Goal: {wk['goal']}", styles["Goal"]))

        bullets = ListFlowable(
            [ListItem(Paragraph(t, styles["Bullet2"]), leftIndent=10, value="•") for t in wk["tasks"]],
            bulletType="bullet", start="•", leftIndent=12,
        )
        story.append(bullets)
        story.append(Paragraph(f"Deliverable: {wk['deliverable']}", styles["Deliver"]))
        story.append(Spacer(1, 12))

    # ── Outcome ──────────────────────────────────────────────────────────────
    story.append(section_rule())
    story.append(Paragraph("Outcome", styles["H2"]))
    outcome = (
        "Over three weeks the project grew from an empty repository into a secure, multi-user "
        "AI product. It combines classical NLP (Spacy NER, PyMuPDF) with a custom machine-learning "
        "classifier for contract-type prediction, all running fully on-device with no external AI "
        "API. The application is protected by JWT authentication, scopes data per user, and ships "
        "with a public landing page and automated PDF reporting."
    )
    story.append(Paragraph(outcome, styles["BodyText2"]))

    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    print(f"[OK] Generated {OUTPUT}")


def _footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(SLATE)
    canvas.drawString(20 * mm, 10 * mm, "LexiScan Auto — Weekly Project Report")
    canvas.drawRightString(190 * mm, 10 * mm, f"Page {doc.page}")
    canvas.restoreState()


if __name__ == "__main__":
    build()
