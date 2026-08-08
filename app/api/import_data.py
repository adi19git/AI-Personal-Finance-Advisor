from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.auth.dependencies import get_current_active_user
from app.services.import_service import process_and_import_file, ImportException

router = APIRouter(prefix="/api/import", tags=["import"])


@router.post("/")
async def upload_transactions(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Upload a CSV or Excel file containing bank transactions.
    """
    if not file.filename.endswith((".csv", ".xls", ".xlsx")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only CSV and Excel files are supported.",
        )
        
    try:
        # FastAPI's UploadFile exposes a file-like object directly
        result = process_and_import_file(db, file.file, file.filename, current_user)
        return result
    except ImportException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during import: {str(e)}",
        )
    finally:
        await file.close()
