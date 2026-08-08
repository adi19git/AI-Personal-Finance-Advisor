from pydantic import BaseModel, Field
from datetime import datetime


class BudgetCreate(BaseModel):
    category_id: int
    monthly_limit: float = Field(gt=0)
    period: str = Field(pattern=r"^\d{4}-\d{2}$")  # "YYYY-MM"


class BudgetUpdate(BaseModel):
    monthly_limit: float | None = Field(default=None, gt=0)


class BudgetResponse(BaseModel):
    id: int
    user_id: int
    category_id: int
    category_name: str | None = None
    monthly_limit: float
    period: str
    spent: float = 0.0  # computed field, not stored
    remaining: float = 0.0
    usage_percent: float = 0.0
    is_over_budget: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}
