import joblib
from sklearn.ensemble import IsolationForest
from pandas import DataFrame

MODEL_PATH = "model_isoforest.joblib"


def train(df: DataFrame, contamination: float = 0.02):
    X = df
    m = IsolationForest(n_estimators=200, contamination=contamination, random_state=42)
    m.fit(X)
    joblib.dump(m, MODEL_PATH)
    return m


def load_model():
    import os
    import joblib

    if not os.path.exists(MODEL_PATH):
        return None
    return joblib.load(MODEL_PATH)


def score(m, X: DataFrame):
    pred = m.predict(X)  # -1 = anomaly, 1 = normal
    score = m.decision_function(X)
    return pred, score
