import pandas as pd
from sklearn.ensemble import IsolationForest


class AnomalyDetector:
    """
    Detects anomalous transactions for a specific user using Isolation Forest.
    It expects a DataFrame containing transactions with features like 'amount'.
    """

    def __init__(self, contamination: float = 0.05):
        # contamination is the proportion of outliers in the data set
        self.model = IsolationForest(
            contamination=contamination, random_state=42, n_estimators=100
        )

    def fit_predict(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Fits the model on the user's historical transactions and predicts anomalies.
        Returns the DataFrame with 'is_anomaly' and 'anomaly_score' columns added.
        """
        if df.empty or len(df) < 5:
            # Not enough data to reliably detect anomalies
            df["is_anomaly"] = False
            df["anomaly_score"] = 1.0
            return df

        # We'll use just the amount for this simple version.
        # More advanced versions could encode category_id or day of week.
        features = df[["amount"]].copy()

        # Fill NaNs if any
        features = features.fillna(0)

        # Fit and predict (-1 is anomaly, 1 is normal)
        predictions = self.model.fit_predict(features)

        # Get anomaly scores (lower means more anomalous)
        scores = self.model.score_samples(features)

        # Map to boolean
        df["is_anomaly"] = predictions == -1
        df["anomaly_score"] = scores

        return df
