from pydantic import BaseModel


class SpendingByCategory(BaseModel):
    category_id: int | None = None
    category_name: str
    total_amount: float
    transaction_count: int
    percentage: float = 0.0


class MonthlyTrend(BaseModel):
    month: str  # "YYYY-MM"
    total_spent: float
    total_income: float
    net: float
    transaction_count: int


class AnomalySummary(BaseModel):
    total_anomalies: int
    anomalies: list[dict]


class DashboardSummary(BaseModel):
    total_balance: float
    total_income: float
    total_expenses: float
    transaction_count: int
    top_categories: list[SpendingByCategory]
    recent_anomalies: list[dict]
    budget_alerts: list[dict]
    recent_transactions: list[dict] = []
