import argparse
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, classification_report
from app.ml.labeling import generate_synthetic_dataset
from app.ml.categorizer import TransactionCategorizer

def main():
    parser = argparse.ArgumentParser(description="Train the Transaction Categorizer model.")
    parser.add_argument("--samples", type=int, default=5000, help="Number of synthetic samples to generate.")
    args = parser.parse_args()

    print(f"Generating {args.samples} synthetic labeled samples...")
    df = generate_synthetic_dataset(args.samples)
    
    print("Splitting data into 80% train / 20% test...")
    # Stratified split to ensure all categories are represented
    X_train, X_test, y_train, y_test = train_test_split(
        df['description'], df['category_name'], 
        test_size=0.2, 
        random_state=42, 
        stratify=df['category_name']
    )
    
    train_df = pd.DataFrame({'description': X_train, 'category_name': y_train})
    
    print("Training model...")
    categorizer = TransactionCategorizer()
    categorizer.train(train_df, save=True)
    
    print("Evaluating model...")
    y_pred = categorizer.predict(X_test.tolist())
    
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average='weighted')
    
    print("\n" + "="*40)
    print("       MODEL EVALUATION METRICS       ")
    print("="*40)
    print(f"Accuracy:  {acc:.4f}")
    print(f"F1 Score:  {f1:.4f}")
    print("="*40 + "\n")
    
    print("Classification Report:")
    print(classification_report(y_test, y_pred))
    
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    
    print(f"\nModel saved to: {categorizer.model_path}")

if __name__ == "__main__":
    import pandas as pd
    main()
