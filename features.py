import pandas as pd

FEATURES = ["PRB_Util", "RRC_Conn", "Throughput_Mbps", "BLER"]


def load_kpi_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = df.dropna(subset=FEATURES).copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


def to_matrix(df: pd.DataFrame) -> pd.DataFrame:
    return df[FEATURES]
