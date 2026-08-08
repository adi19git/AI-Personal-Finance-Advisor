from pydantic import BaseModel, Field
from datetime import date, datetime


class TransactionCreate(BaseModel):
    date: date
    description: str = Field(min_length=1, max_length=500)
    amount: float
    transaction_type: str = Field(default="debit", pattern="^(debit|credit)$")
    merchant: str | None = None
    category_id: int | None = None
    notes: str | None = None


class TransactionUpdate(BaseModel):
    description: str | None = None
    amount: float | None = None
    transaction_type: str | None = None
    merchant: str | None = None
    category_id: int | None = None
    notes: str | None = None
    # When user corrects the ML-assigned category
    user_corrected: bool | None = None


class TransactionResponse(BaseModel):
    id: int
    user_id: int
    date: date
    description: str
    amount: float
    transaction_type: str
    merchant: str | None = None
    category_id: int | None = None
    category_name: str | None = None
    is_anomaly: bool
    anomaly_score: float | None = None
    notes: str | None = None
    user_corrected: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TransactionFilter(BaseModel):
    start_date: date | None = None
    end_date: date | None = None
    category_id: int | None = None
    transaction_type: str | None = None
    min_amount: float | None = None
    max_amount: float | None = None
    is_anomaly: bool | None = None
