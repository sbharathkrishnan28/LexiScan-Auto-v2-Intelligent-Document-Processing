"""
Offline contract-type classifier.

A lightweight, fully-offline machine-learning model (TF-IDF + Logistic
Regression, scikit-learn) that *predicts the category* of an uploaded contract
from its raw text — no external API, no internet, no API key.

The model is trained once from a small embedded labelled corpus and cached to
disk via joblib. On subsequent imports it loads instantly from the cache.

Public API:
    predict(text) -> dict   # category + confidence + ranked probabilities
"""

import os
import re
import joblib
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "contract_clf.joblib")

# Human-readable description shown in the UI for each predicted class.
CATEGORY_INFO = {
    "NDA": "Non-Disclosure / Confidentiality Agreement",
    "Employment": "Employment / Offer Agreement",
    "Lease": "Lease / Rental Agreement",
    "Service": "Service / Consulting Agreement",
    "Sales": "Sales / Purchase Agreement",
    "Loan": "Loan / Financing Agreement",
}

# ── Embedded training corpus ─────────────────────────────────────────────────
# Short, representative snippets per class. Small but enough for a TF-IDF model
# to separate the vocabulary of common contract families for a demo/portfolio.
_TRAINING_DATA = [
    # NDA
    ("This Non-Disclosure Agreement governs the exchange of confidential information between the disclosing party and the receiving party.", "NDA"),
    ("The receiving party agrees to keep all proprietary and confidential information secret and not to disclose trade secrets.", "NDA"),
    ("Each party shall protect confidential information and use it solely for the permitted purpose of evaluating the business relationship.", "NDA"),
    ("This mutual confidentiality agreement covers proprietary data, trade secrets, and non-public information disclosed during discussions.", "NDA"),
    ("The recipient shall not reproduce or disclose any confidential materials to third parties without prior written consent.", "NDA"),
    ("Confidential information includes business plans, customer lists, and any non-public technical or financial information.", "NDA"),

    # Employment
    ("This Employment Agreement sets out the terms of employment, salary, job title, and benefits for the employee.", "Employment"),
    ("The employee shall be paid an annual base salary and is entitled to paid vacation, health insurance, and other benefits.", "Employment"),
    ("This offer letter outlines your position, start date, compensation, reporting manager, and at-will employment terms.", "Employment"),
    ("The employee agrees to perform the duties of the role and comply with company policies during the term of employment.", "Employment"),
    ("Compensation includes base salary, performance bonus, stock options, and is subject to standard payroll deductions.", "Employment"),
    ("Either the employer or employee may terminate this employment relationship with two weeks written notice.", "Employment"),

    # Lease
    ("This Lease Agreement is made between the landlord and the tenant for the rental of the residential property.", "Lease"),
    ("The tenant agrees to pay monthly rent and a security deposit for occupancy of the leased premises.", "Lease"),
    ("The landlord shall maintain the premises while the tenant is responsible for utilities during the lease term.", "Lease"),
    ("This rental agreement covers the apartment unit, the monthly rent amount, and the lease commencement date.", "Lease"),
    ("The tenant shall not sublet the premises without the landlord's prior written consent under this tenancy.", "Lease"),
    ("Upon expiration of the lease, the tenant shall vacate the property and return all keys to the landlord.", "Lease"),

    # Service
    ("This Service Agreement defines the scope of services, deliverables, and fees the service provider will deliver to the client.", "Service"),
    ("The consultant shall provide professional consulting services and invoice the client on a monthly basis.", "Service"),
    ("This master services agreement governs statements of work, deliverables, milestones, and payment terms between the parties.", "Service"),
    ("The contractor agrees to perform the services described in the statement of work for the agreed project fee.", "Service"),
    ("The service provider warrants that all deliverables will conform to the specifications set forth in this agreement.", "Service"),
    ("Payment for services rendered shall be due within thirty days of receipt of a valid invoice.", "Service"),

    # Sales
    ("This Sales Agreement covers the purchase and sale of goods between the seller and the buyer at the agreed price.", "Sales"),
    ("The seller agrees to deliver the products and the buyer agrees to pay the purchase price upon delivery.", "Sales"),
    ("This purchase agreement sets the quantity, unit price, delivery schedule, and warranty for the goods sold.", "Sales"),
    ("Title and risk of loss for the goods shall pass to the buyer upon shipment from the seller's warehouse.", "Sales"),
    ("The buyer shall inspect the goods upon delivery and notify the seller of any defects within ten days.", "Sales"),
    ("This agreement for the sale of equipment includes the total purchase price, taxes, and payment installments.", "Sales"),

    # Loan
    ("This Loan Agreement sets out the principal amount, interest rate, and repayment schedule between the lender and the borrower.", "Loan"),
    ("The borrower agrees to repay the loan principal plus accrued interest in monthly installments to the lender.", "Loan"),
    ("This promissory note evidences the borrower's obligation to repay the loaned funds with interest by the maturity date.", "Loan"),
    ("The lender shall advance the loan amount and the borrower shall provide collateral to secure the indebtedness.", "Loan"),
    ("Default occurs if the borrower fails to make any scheduled loan repayment of principal or interest when due.", "Loan"),
    ("The annual percentage rate, finance charge, and total amount financed are disclosed under this credit agreement.", "Loan"),
]


def _train_model() -> Pipeline:
    texts = [t for t, _ in _TRAINING_DATA]
    labels = [l for _, l in _TRAINING_DATA]

    model = Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2),
            stop_words="english",
            sublinear_tf=True,
            min_df=1,
        )),
        ("clf", LogisticRegression(max_iter=1000, C=4.0)),
    ])
    model.fit(texts, labels)
    return model


def _load_or_train() -> Pipeline:
    if os.path.exists(MODEL_PATH):
        try:
            return joblib.load(MODEL_PATH)
        except Exception:
            pass  # corrupt/incompatible cache — retrain
    model = _train_model()
    try:
        joblib.dump(model, MODEL_PATH)
    except Exception:
        pass  # read-only fs — keep in-memory model
    return model


# Trained once at import, then cached.
_MODEL = _load_or_train()


def predict(text: str) -> dict:
    """Predict the contract category for a block of text.

    Returns a dict with the top category, a 0-100 confidence, a friendly
    description, and the full ranked probability distribution.
    """
    cleaned = re.sub(r"\s+", " ", (text or "")).strip()

    if len(cleaned) < 20:
        return {
            "category": "Unknown",
            "category_label": "Insufficient text to classify",
            "confidence": 0,
            "ranked": [],
        }

    proba = _MODEL.predict_proba([cleaned])[0]
    classes = _MODEL.named_steps["clf"].classes_

    ranked = sorted(
        ({"category": c, "probability": round(float(p) * 100, 1)} for c, p in zip(classes, proba)),
        key=lambda x: x["probability"],
        reverse=True,
    )

    top = ranked[0]
    return {
        "category": top["category"],
        "category_label": CATEGORY_INFO.get(top["category"], top["category"]),
        "confidence": round(top["probability"]),
        "ranked": ranked,
    }


if __name__ == "__main__":
    # Quick smoke test
    samples = [
        "The tenant shall pay monthly rent to the landlord for the apartment.",
        "The receiving party shall keep all confidential trade secrets private.",
        "The borrower agrees to repay the loan principal with interest to the lender.",
    ]
    for s in samples:
        r = predict(s)
        print(f"{r['category']:12} {r['confidence']:>3}%  <- {s[:55]}")
