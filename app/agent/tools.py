"""
LangChain tools that the AI agent can invoke to query the user's financial data.
Each tool wraps a service function and returns structured text for the LLM.
"""
from langchain_core.tools import tool
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from app.models.transaction import Transaction
from app.models.category import Category
from app.models.budget import Budget


def _get_tools(db: Session, user_id: int):
    """
    Returns a list of LangChain tools bound to a specific DB session and user.
    This closure pattern ensures each tool operates on the correct user's data.
    """

    @tool
    def get_spending_summary(period: str = "") -> str:
        """
        Get a summary of the user's spending. Optionally filter by period (YYYY-MM).
        Returns total income, expenses, balance, and top categories.
        """
        query = db.query(Transaction).filter(Transaction.user_id == user_id)

        if period:
            try:
                year, month = map(int, period.split("-"))
                query = query.filter(
                    extract("year", Transaction.date) == year,
                    extract("month", Transaction.date) == month,
                )
            except ValueError:
                return "Invalid period format. Use YYYY-MM."

        total_income = (
            query.filter(Transaction.transaction_type == "credit")
            .with_entities(func.sum(Transaction.amount))
            .scalar()
            or 0.0
        )
        total_expense = (
            query.filter(Transaction.transaction_type == "debit")
            .with_entities(func.sum(Transaction.amount))
            .scalar()
            or 0.0
        )

        # Top 5 categories by spend
        top_cats = (
            db.query(Category.name, func.sum(Transaction.amount).label("total"))
            .join(Transaction, Transaction.category_id == Category.id)
            .filter(Transaction.user_id == user_id, Transaction.transaction_type == "debit")
            .group_by(Category.name)
            .order_by(func.sum(Transaction.amount).desc())
            .limit(5)
            .all()
        )

        cats_str = "\n".join(
            [f"  - {name}: ₹{total:.2f}" for name, total in top_cats]
        ) or "  No category data."

        period_label = f" for {period}" if period else " (all time)"
        return (
            f"Spending Summary{period_label}:\n"
            f"  Total Income: ₹{total_income:.2f}\n"
            f"  Total Expenses: ₹{total_expense:.2f}\n"
            f"  Net Balance: ₹{total_income - total_expense:.2f}\n"
            f"  Transaction Count: {query.count()}\n\n"
            f"Top Spending Categories:\n{cats_str}"
        )

    @tool
    def get_budget_status(period: str) -> str:
        """
        Get budget status for a specific period (YYYY-MM).
        Shows each budget's limit, spent amount, and whether over budget.
        """
        budgets = (
            db.query(Budget)
            .filter(Budget.user_id == user_id, Budget.period == period)
            .all()
        )
        if not budgets:
            return f"No budgets set for {period}."

        try:
            year, month = map(int, period.split("-"))
        except ValueError:
            return "Invalid period format. Use YYYY-MM."

        lines = [f"Budget Status for {period}:"]
        for b in budgets:
            spent = (
                db.query(func.sum(Transaction.amount))
                .filter(
                    Transaction.user_id == user_id,
                    Transaction.category_id == b.category_id,
                    Transaction.transaction_type == "debit",
                    extract("year", Transaction.date) == year,
                    extract("month", Transaction.date) == month,
                )
                .scalar()
                or 0.0
            )
            cat_name = db.query(Category.name).filter(Category.id == b.category_id).scalar() or "Unknown"
            status = "🔴 OVER BUDGET" if spent > b.monthly_limit else "🟢 OK"
            lines.append(
                f"  {cat_name}: ₹{spent:.2f} / ₹{b.monthly_limit:.2f} ({status})"
            )
        return "\n".join(lines)

    @tool
    def get_recent_transactions(count: str = "10") -> str:
        """
        Get the most recent transactions for the user.
        Returns date, description, amount, type, and category.
        Args:
            count: Number of transactions to return (default "10").
        """
        try:
            n = int(count)
        except (ValueError, TypeError):
            n = 10
        txs = (
            db.query(Transaction)
            .filter(Transaction.user_id == user_id)
            .order_by(Transaction.date.desc())
            .limit(n)
            .all()
        )
        if not txs:
            return "No transactions found."

        lines = [f"Last {len(txs)} Transactions:"]
        for t in txs:
            cat_name = ""
            if t.category_id:
                cat_name = db.query(Category.name).filter(Category.id == t.category_id).scalar() or ""
            anomaly_flag = " ⚠️ ANOMALY" if t.is_anomaly else ""
            lines.append(
                f"  {t.date} | {t.description[:40]} | ₹{t.amount:.2f} | {t.transaction_type} | {cat_name}{anomaly_flag}"
            )
        return "\n".join(lines)

    @tool
    def get_anomalies() -> str:
        """
        Get all anomalous (unusual) transactions flagged by the system.
        """
        anomalies = (
            db.query(Transaction)
            .filter(Transaction.user_id == user_id, Transaction.is_anomaly == True)
            .order_by(Transaction.date.desc())
            .all()
        )
        if not anomalies:
            return "No anomalous transactions detected."

        lines = ["Anomalous Transactions:"]
        for a in anomalies:
            lines.append(
                f"  {a.date} | {a.description} | ₹{a.amount:.2f} | score: {a.anomaly_score:.3f}"
            )
        return "\n".join(lines)

    return [get_spending_summary, get_budget_status, get_recent_transactions, get_anomalies]
