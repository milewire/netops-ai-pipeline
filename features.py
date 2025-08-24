import pandas as pd

FEATURES = ["PRB_Util", "RRC_Conn", "Throughput_Mbps", "BLER"]


def load_kpi_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    
    # Validate required columns
    required_columns = ["cell_id", "timestamp"] + FEATURES
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    
    df = df.dropna(subset=FEATURES).copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


def to_matrix(df: pd.DataFrame) -> pd.DataFrame:
    return df[FEATURES]
