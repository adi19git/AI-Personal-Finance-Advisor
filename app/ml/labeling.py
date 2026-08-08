import pandas as pd
import random
from typing import List, Dict

# Rule-based keywords mapping to categories
# Used to seed a synthetic dataset for training our ML categorizer
CATEGORY_RULES: Dict[str, List[str]] = {
    "Food & Dining": ["zomato", "swiggy", "mcdonalds", "kfc", "starbucks", "dominos", "cafe", "restaurant", "pizza", "burger king"],
    "Groceries": ["blinkit", "zepto", "instamart", "bigbasket", "dmart", "reliance fresh", "supermarket", "grocery"],
    "Transport": ["uber", "ola", "rapido", "metro", "irctc", "fuel", "petrol", "indian oil", "bharat petroleum", "shell", "fastag"],
    "Utilities": ["electricity", "water bill", "jio", "airtel", "vi", "broadband", "recharge", "gas", "bescom", "mahavitaran"],
    "Shopping": ["amazon", "flipkart", "myntra", "ajio", "zara", "h&m", "nykaa", "shoppers stop", "lifestyle", "apparel"],
    "Entertainment": ["netflix", "amazon prime", "spotify", "bookmyshow", "pvr", "inox", "hotstar", "youtube premium", "steam", "playstation"],
    "Health & Fitness": ["pharmacy", "apollo", "1mg", "practo", "gym", "cult.fit", "hospital", "clinic", "health insurance"],
    "Housing": ["rent", "maintenance", "brokerage", "home loan", "emi", "furniture", "ikea", "urban company"],
    "Income": ["salary", "payroll", "neft", "rtgs", "dividend", "interest", "refund", "cashback", "freelance"],
    "Transfer": ["atm withdrawal", "upi transfer", "self transfer", "paytm", "gpay", "phonepe", "splitwise"],
}

# Prefixes and suffixes to add noise to synthetic transactions
PREFIXES = ["UPI-", "POS ", "NEFT ", "RTGS-", "IMPS-", "PURCHASE ", "PAYMENT TO ", ""]
SUFFIXES = [" /MUMBAI", " /DELHI", " /BLR", " - TXN", " 1234", " 9876", ""]

def generate_synthetic_dataset(num_samples: int = 1000) -> pd.DataFrame:
    """
    Generates a synthetic labeled dataset of transaction descriptions and categories
    based on predefined keywords and random noise, to bootstrap our ML model.
    """
    data = []
    categories = list(CATEGORY_RULES.keys())
    
    for _ in range(num_samples):
        # Pick a random category
        cat = random.choice(categories)
        
        # Pick a base keyword for that category
        keyword = random.choice(CATEGORY_RULES[cat])
        
        # Add random capitalization and noise to simulate real bank statements
        if random.random() > 0.5:
            keyword = keyword.upper()
        elif random.random() > 0.5:
            keyword = keyword.title()
            
        prefix = random.choice(PREFIXES)
        suffix = random.choice(SUFFIXES)
        
        # Sometimes append random numbers/dates
        if random.random() > 0.7:
            date_str = f"{random.randint(1, 30):02d}{random.randint(1, 12):02d}"
            description = f"{prefix}{keyword}{suffix} {date_str}"
        else:
            description = f"{prefix}{keyword}{suffix}"
            
        data.append({
            "description": description,
            "category_name": cat
        })
        
    return pd.DataFrame(data)

if __name__ == "__main__":
    # Test generation
    df = generate_synthetic_dataset(10)
    print(df)
