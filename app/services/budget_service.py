from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from app.models.budget import Budget
from app.models.transaction import Transaction
from app.models.category import Category
from app.schemas.budget import BudgetCreate, BudgetUpdate, BudgetResponse


class BudgetService:
    @staticmethod
    def get_budgets_for_period(db: Session, user_id: int, period: str) -> list[BudgetResponse]:
        """
        Gets all budgets for a user for a specific period (YYYY-MM),
        and calculates the 'spent', 'remaining', 'usage_percent', and 'is_over_budget'.
        """
        budgets = (
            db.query(Budget)
            .filter(Budget.user_id == user_id, Budget.period == period)
            .all()
        )

        year, month = map(int, period.split("-"))

        result = []
        for budget in budgets:
            import calendar
            import datetime
            last_day = calendar.monthrange(year, month)[1]
            start_date = datetime.date(year, month, 1)
            end_date = datetime.date(year, month, last_day)
            
            spent = (
                db.query(func.sum(Transaction.amount))
                .filter(
                    Transaction.user_id == user_id,
                    Transaction.category_id == budget.category_id,
                    Transaction.transaction_type == "debit",
                    Transaction.date >= start_date,
                    Transaction.date <= end_date,
                )
                .scalar()
                or 0.0
            )

            remaining = budget.monthly_limit - spent
            usage_percent = (spent / budget.monthly_limit) * 100 if budget.monthly_limit > 0 else 0
            is_over_budget = spent > budget.monthly_limit

            category_name = (
                 db.query(Category.name)
                 .filter(Category.id == budget.category_id)
                 .scalar()
            )

            result.append(
                BudgetResponse(
                    id=budget.id,
                    user_id=budget.user_id,
                    category_id=budget.category_id,
                    category_name=category_name,
                    monthly_limit=budget.monthly_limit,
                    period=budget.period,
                    spent=spent,
                    remaining=remaining,
                    usage_percent=usage_percent,
                    is_over_budget=is_over_budget,
                    created_at=budget.created_at,
                )
            )

        return result

    @staticmethod
    def create_budget(db: Session, user_id: int, budget_in: BudgetCreate) -> Budget:
        # Check if one already exists for this category and period
        existing = (
            db.query(Budget)
            .filter(
                Budget.user_id == user_id,
                Budget.category_id == budget_in.category_id,
                Budget.period == budget_in.period,
            )
            .first()
        )
        if existing:
            raise ValueError(f"Budget already exists for this category in period {budget_in.period}.")

        budget = Budget(
            user_id=user_id,
            category_id=budget_in.category_id,
            monthly_limit=budget_in.monthly_limit,
            period=budget_in.period,
        )
        db.add(budget)
        db.commit()
        db.refresh(budget)
        return budget

    @staticmethod
    def update_budget(db: Session, user_id: int, budget_id: int, budget_in: BudgetUpdate) -> Budget:
        budget = (
            db.query(Budget)
            .filter(Budget.id == budget_id, Budget.user_id == user_id)
            .first()
        )
        if not budget:
             raise ValueError("Budget not found.")

        if budget_in.monthly_limit is not None:
             budget.monthly_limit = budget_in.monthly_limit

        db.commit()
        db.refresh(budget)
        return budget

    @staticmethod
    def delete_budget(db: Session, user_id: int, budget_id: int):
         budget = (
            db.query(Budget)
            .filter(Budget.id == budget_id, Budget.user_id == user_id)
            .first()
         )
         if not budget:
             raise ValueError("Budget not found.")
         db.delete(budget)
         db.commit()
