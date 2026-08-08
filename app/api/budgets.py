from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.auth.dependencies import get_current_active_user
from app.schemas.budget import BudgetCreate, BudgetUpdate, BudgetResponse
from app.services.budget_service import BudgetService

router = APIRouter(prefix="/api/budgets", tags=["budgets"])


@router.get("/", response_model=list[BudgetResponse])
def get_budgets(
    period: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get all budgets for a specific period (YYYY-MM) for the current user.
    """
    return BudgetService.get_budgets_for_period(db, current_user.id, period)


@router.post("/", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
def create_budget(
    budget_in: BudgetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Create a new budget for a category in a specific period.
    """
    try:
        budget = BudgetService.create_budget(db, current_user.id, budget_in)
        # Fetch it back through the service to get the calculated fields
        budgets = BudgetService.get_budgets_for_period(db, current_user.id, budget.period)
        return next(b for b in budgets if b.id == budget.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{budget_id}", response_model=BudgetResponse)
def update_budget(
    budget_id: int,
    budget_in: BudgetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Update a budget's monthly limit.
    """
    try:
        budget = BudgetService.update_budget(db, current_user.id, budget_id, budget_in)
        budgets = BudgetService.get_budgets_for_period(db, current_user.id, budget.period)
        return next(b for b in budgets if b.id == budget.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget(
    budget_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Delete a budget.
    """
    try:
        BudgetService.delete_budget(db, current_user.id, budget_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
