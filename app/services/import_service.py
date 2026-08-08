import pandas as pd
from typing import BinaryIO
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.transaction import Transaction
from app.models.user import User


class ImportException(Exception):
    pass


def normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalizes dataframe columns to expected names: 'date', 'description', 'amount', 'transaction_type'.
    Handles common variations in bank statement CSVs.
    """
    # Lowercase and strip column names
    df.columns = [col.lower().strip() for col in df.columns]

    # Map common column names
    col_mapping = {
        "date": ["date", "transaction date", "posted date"],
        "description": ["description", "narrative", "payee", "particulars", "details"],
        "amount": ["amount", "value", "debit/credit", "transaction amount"],
        # Sometimes debit/credit are split
        "debit": ["debit", "withdrawal", "spent"],
        "credit": ["credit", "deposit", "received"],
    }

    normalized = pd.DataFrame()

    # Find Date
    for possible_name in col_mapping["date"]:
        if possible_name in df.columns:
            # Coerce to datetime, invalid formats become NaT (Not a Time)
            normalized["date"] = pd.to_datetime(df[possible_name], errors="coerce").dt.date
            break
    if "date" not in normalized:
        raise ImportException("Could not find a valid 'Date' column.")

    # Find Description
    for possible_name in col_mapping["description"]:
        if possible_name in df.columns:
            normalized["description"] = df[possible_name].fillna("").astype(str)
            break
    if "description" not in normalized:
        raise ImportException("Could not find a valid 'Description' column.")

    # Handle Amount and Transaction Type
    type_col = next((c for c in ["transaction type", "type"] if c in df.columns), None)
    
    if any(name in df.columns for name in col_mapping["amount"]):
        for name in col_mapping["amount"]:
            if name in df.columns:
                # Remove currency symbols and commas before converting
                raw_amount = df[name].astype(str).str.replace(r"[^\d\.\-]", "", regex=True)
                amount_series = pd.to_numeric(raw_amount, errors="coerce")
                
                normalized["amount"] = amount_series.abs()
                
                if type_col:
                    normalized["transaction_type"] = df[type_col].str.lower().str.strip()
                else:
                    # Determine type: less than 0 is usually debit if signed
                    normalized["transaction_type"] = amount_series.apply(
                        lambda x: "debit" if x < 0 else "credit"
                    )
                break
    else:
        # Check if split into Debit / Credit
        debit_col = next((c for c in col_mapping["debit"] if c in df.columns), None)
        credit_col = next((c for c in col_mapping["credit"] if c in df.columns), None)

        if not debit_col and not credit_col:
             raise ImportException("Could not find Amount, Debit, or Credit columns.")

        normalized["amount"] = 0.0
        normalized["transaction_type"] = "debit"

        for idx, row in df.iterrows():
            d_val = pd.to_numeric(str(row.get(debit_col, "")).replace(",", ""), errors="coerce") if debit_col else pd.isna
            c_val = pd.to_numeric(str(row.get(credit_col, "")).replace(",", ""), errors="coerce") if credit_col else pd.isna
            
            d_val = d_val if not pd.isna(d_val) else 0.0
            c_val = c_val if not pd.isna(c_val) else 0.0

            if d_val > 0:
                normalized.loc[idx, "amount"] = abs(d_val)
                normalized.loc[idx, "transaction_type"] = "debit"
            elif c_val > 0:
                normalized.loc[idx, "amount"] = abs(c_val)
                normalized.loc[idx, "transaction_type"] = "credit"
            else:
                 # Default if both 0 or empty
                 normalized.loc[idx, "amount"] = 0.0
                 normalized.loc[idx, "transaction_type"] = "debit"
                 
    # Drop rows where date or amount is null
    normalized = normalized.dropna(subset=["date", "amount"])
    
    return normalized


from app.ml.categorizer import TransactionCategorizer
from app.models.category import Category

def get_or_create_category(db: Session, category_name: str) -> int:
    cat = db.query(Category).filter(Category.name == category_name).first()
    if cat:
        return cat.id
    
    # Create new category
    new_cat = Category(name=category_name, is_default=False)
    db.add(new_cat)
    db.commit()
    db.refresh(new_cat)
    return new_cat.id

def process_and_import_file(db: Session, file_obj: BinaryIO, filename: str, user: User) -> dict:
    """
    Reads CSV/XLSX, normalizes data, uses ML to predict category, and bulk inserts.
    """
    try:
        if filename.endswith(".csv"):
            df = pd.read_csv(file_obj)
        elif filename.endswith((".xls", ".xlsx")):
            df = pd.read_excel(file_obj)
        else:
            raise ImportException("Unsupported file format. Please upload CSV or Excel.")
    except Exception as e:
         raise ImportException(f"Error reading file: {str(e)}")

    if df.empty:
        raise ImportException("The uploaded file is empty.")

    normalized_df = normalize_dataframe(df)

    # Initialize ML categorizer
    categorizer = TransactionCategorizer()
    
    # Batch predict categories
    descriptions = normalized_df["description"].tolist()
    predicted_categories = categorizer.predict(descriptions)
    
    # Run anomaly detection
    from app.ml.anomaly_detector import AnomalyDetector
    detector = AnomalyDetector()
    normalized_df = detector.fit_predict(normalized_df)

    # Cache category IDs to minimize DB queries
    category_id_cache = {}

    transactions_to_insert = []
    for idx, row in normalized_df.iterrows():
        cat_name = predicted_categories[idx]
        
        if cat_name not in category_id_cache:
            category_id_cache[cat_name] = get_or_create_category(db, cat_name)
            
        category_id = category_id_cache[cat_name]
        
        trx = Transaction(
            user_id=user.id,
            date=row["date"],
            description=row["description"][:500],
            amount=float(row["amount"]),
            transaction_type=row["transaction_type"],
            category_id=category_id,
            is_anomaly=bool(row.get("is_anomaly", False)),
            anomaly_score=float(row.get("anomaly_score", 1.0))
        )
        transactions_to_insert.append(trx)

    if not transactions_to_insert:
         raise ImportException("No valid transactions found to import.")

    db.bulk_save_objects(transactions_to_insert)
    db.commit()

    # Build a response with transaction details for the UI
    # Invert category_id_cache for lookup
    id_to_category = {v: k for k, v in category_id_cache.items()}

    imported_data = []
    for trx in transactions_to_insert:
        imported_data.append({
            "date": str(trx.date),
            "description": trx.description,
            "amount": trx.amount,
            "type": trx.transaction_type,
            "category": id_to_category.get(trx.category_id, "Unknown"),
            "is_anomaly": trx.is_anomaly,
            "anomaly_score": round(trx.anomaly_score, 3) if trx.anomaly_score else None,
        })

    return {
        "message": f"Successfully imported {len(transactions_to_insert)} transactions.",
        "count": len(transactions_to_insert),
        "transactions": imported_data,
    }
