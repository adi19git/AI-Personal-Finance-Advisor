from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.transaction import Transaction
from app.models.category import Category
from app.schemas.analytics import DashboardSummary, SpendingByCategory, MonthlyTrend

class AnalyticsService:
    @staticmethod
    def get_dashboard_summary(db: Session, user_id: int) -> DashboardSummary:
        """
        Gets high-level metrics for the user dashboard.
        """
        # Income vs Expense total
        total_income = db.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id, 
            Transaction.transaction_type == "credit"
        ).scalar() or 0.0
        
        total_expense = db.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id, 
            Transaction.transaction_type == "debit"
        ).scalar() or 0.0

        total_balance = total_income - total_expense
        
        transaction_count = db.query(Transaction).filter(Transaction.user_id == user_id).count()

        # Top spending categories
        top_cats = (
            db.query(
                Category.id, 
                Category.name, 
                func.sum(Transaction.amount).label("total_amount"),
                func.count(Transaction.id).label("transaction_count")
            )
            .join(Transaction, Transaction.category_id == Category.id)
            .filter(Transaction.user_id == user_id, Transaction.transaction_type == "debit")
            .group_by(Category.id)
            .order_by(func.sum(Transaction.amount).desc())
            .limit(5)
            .all()
        )

        categories_summary = []
        for cat in top_cats:
            percentage = (cat.total_amount / total_expense * 100) if total_expense > 0 else 0
            categories_summary.append(SpendingByCategory(
                category_id=cat.id,
                category_name=cat.name,
                total_amount=cat.total_amount,
                transaction_count=cat.transaction_count,
                percentage=percentage
            ))

        # Recent anomalies
        anomalies = (
            db.query(Transaction)
            .filter(Transaction.user_id == user_id, Transaction.is_anomaly == True)
            .order_by(Transaction.date.desc())
            .limit(5)
            .all()
        )
        recent_anomalies = [
             {
                 "id": a.id,
                 "date": a.date.strftime("%Y-%m-%d"),
                 "description": a.description,
                 "amount": a.amount,
                 "transaction_type": a.transaction_type,
                 "anomaly_score": a.anomaly_score,
                 "category_name": a.category.name if a.category else "Uncategorized"
             } for a in anomalies
        ]

        # Recent transactions (normal)
        recent_txs = (
            db.query(Transaction)
            .filter(Transaction.user_id == user_id)
            .order_by(Transaction.date.desc(), Transaction.id.desc())
            .limit(10)
            .all()
        )
        recent_transactions = [
             {
                 "id": t.id,
                 "date": t.date.strftime("%Y-%m-%d"),
                 "description": t.description,
                 "amount": t.amount,
                 "transaction_type": t.transaction_type,
                 "is_anomaly": t.is_anomaly,
                 "category_name": t.category.name if t.category else "Uncategorized"
             } for t in recent_txs
        ]

        return DashboardSummary(
            total_balance=total_balance,
            total_income=total_income,
            total_expenses=total_expense,
            transaction_count=transaction_count,
            top_categories=categories_summary,
            recent_anomalies=recent_anomalies,
            budget_alerts=[], # To be populated if needed
            recent_transactions=recent_transactions
        )
