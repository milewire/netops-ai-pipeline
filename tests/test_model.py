import pandas as pd
from model import train, load_model, score


def test_model_training():
    df = pd.DataFrame(
        {
            "PRB_Util": [45.2, 48.1, 52.3, 44.8, 90.5],  # Last one is anomaly
            "RRC_Conn": [150, 155, 140, 148, 50],  # Last one is anomaly
            "Throughput_Mbps": [25.5, 26.1, 24.8, 25.2, 5.1],  # Last one is anomaly
            "BLER": [0.02, 0.03, 0.01, 0.02, 0.15],  # Last one is anomaly
        }
    )

    model = train(df, contamination=0.2)  # Expect 20% anomalies
    assert model is not None

    pred, scores = score(model, df)
    assert len(pred) == len(df)
    assert len(scores) == len(df)
    assert all(p in [-1, 1] for p in pred)  # -1 = anomaly, 1 = normal


def test_model_persistence():
    df = pd.DataFrame(
        {
            "PRB_Util": [45.2, 48.1, 52.3],
            "RRC_Conn": [150, 155, 140],
            "Throughput_Mbps": [25.5, 26.1, 24.8],
            "BLER": [0.02, 0.03, 0.01],
        }
    )

    train(df)

    loaded_model = load_model()
    assert loaded_model is not None

    pred, scores = score(loaded_model, df)
    assert len(pred) == len(df)
