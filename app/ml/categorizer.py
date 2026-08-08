import os
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from app.config import get_settings

settings = get_settings()

MODEL_FILENAME = "transaction_categorizer.joblib"

class TransactionCategorizer:
    """
    ML model for categorizing transactions based on their descriptions.
    Uses TF-IDF for text vectorization and Logistic Regression for classification.
    """
    
    def __init__(self):
        self.model_path = os.path.join(settings.ml_model_dir, MODEL_FILENAME)
        self.pipeline = None
        self._load_model_if_exists()
        
    def _load_model_if_exists(self):
        if os.path.exists(self.model_path):
            try:
                self.pipeline = joblib.load(self.model_path)
            except Exception as e:
                print(f"Warning: Failed to load existing model: {e}")
                self.pipeline = None

    def train(self, df: pd.DataFrame, save: bool = True):
        """
        Trains the TF-IDF + Logistic Regression pipeline on a labeled DataFrame.
        Expected columns: 'description', 'category_name'
        """
        if df.empty or 'description' not in df.columns or 'category_name' not in df.columns:
            raise ValueError("Training DataFrame must contain 'description' and 'category_name' columns.")
            
        X = df['description'].astype(str)
        y = df['category_name'].astype(str)
        
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(
                analyzer='word',
                ngram_range=(1, 3),   # Unigrams, bigrams, trigrams
                stop_words='english',
                max_features=5000,
                sublinear_tf=True
            )),
            ('clf', LogisticRegression(
                C=1.0, 
                class_weight='balanced', 
                solver='lbfgs', 
                max_iter=1000
            ))
        ])
        
        self.pipeline.fit(X, y)
        
        if save:
            self.save_model()
            
        return self

    def predict(self, descriptions: list[str]) -> list[str]:
        """
        Predicts categories for a list of transaction descriptions.
        If the model is not trained, returns 'Uncategorized' for all.
        """
        if not self.pipeline:
            # Fallback if no model is trained yet
            return ["Uncategorized"] * len(descriptions)
            
        # Ensure strings
        X = [str(d) for d in descriptions]
        predictions = self.pipeline.predict(X)
        return predictions.tolist()
        
    def predict_single(self, description: str) -> str:
        """Convenience method for a single prediction."""
        return self.predict([description])[0]
        
    def save_model(self):
        """Saves the trained pipeline to disk."""
        if not self.pipeline:
            raise RuntimeError("Cannot save an untrained model.")
            
        os.makedirs(settings.ml_model_dir, exist_ok=True)
        joblib.dump(self.pipeline, self.model_path)
