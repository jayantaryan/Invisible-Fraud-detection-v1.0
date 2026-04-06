import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from utils import load_model, rule_based_risk, combine_risk, prepare_features

app = FastAPI(
    title="Invisible Fraud Detector",
    description="A lightweight FastAPI service that combines an ML model and behavior rules to score fraud risk.",
    version="1.0.0",
)

# Use CORS so the frontend can call this backend from its local port.
origins = ["http://127.0.0.1:5173", "http://localhost:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load or train the model the first time the server starts.
model = load_model()


class TransactionInput(BaseModel):
    amount: float = Field(..., gt=0, description="Transaction amount in dollars")
    hour: int = Field(..., ge=0, le=23, description="Hour of day in 24-hour format")
    location_change: int = Field(..., ge=0, le=1, description="1 when location changed")
    device_change: int = Field(..., ge=0, le=1, description="1 when device changed")
    transaction_type: str = Field(..., description="Transaction channel: online, pos, or atm")

    @validator("transaction_type")
    def validate_transaction_type(cls, value):
        normalized = value.lower()
        if normalized not in {"online", "pos", "atm"}:
            raise ValueError("transaction_type must be online, pos, or atm")
        return normalized


@app.post("/check")
def check_transaction(transaction: TransactionInput):
    """Evaluate a transaction and return a combined fraud risk score."""
    try:
        features = prepare_features(transaction)
        ml_probability = float(model.predict_proba([features])[0][1])
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    rule_score, reasons = rule_based_risk(transaction)
    risk_score = combine_risk(ml_probability, rule_score)

    status = "FRAUD" if risk_score >= 0.5 else "SAFE"

    if not reasons:
        reasons = ["No behavior-based risk flags detected"]

    # Add a short explanation from the ML model.
    reasons.append(f"Model confidence for fraud: {ml_probability:.2f}")

    return {
        "risk_score": round(risk_score, 3),
        "status": status,
        "reasons": reasons,
    }
