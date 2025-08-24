import pandas as pd
from features import to_matrix, FEATURES, load_kpi_csv
import tempfile
import os


def test_to_matrix_columns():
    df = pd.DataFrame(
        {"PRB_Util": [1], "RRC_Conn": [2], "Throughput_Mbps": [3], "BLER": [0.1]}
    )
    X = to_matrix(df)
    assert list(X.columns) == FEATURES


def test_load_kpi_csv():
    csv_content = """cell_id,timestamp,PRB_Util,RRC_Conn,Throughput_Mbps,BLER
CELL001,2024-01-01 10:00:00,45.2,150,25.5,0.02
CELL001,2024-01-01 10:01:00,48.1,155,26.1,0.03
CELL002,2024-01-01 10:00:00,52.3,140,24.8,0.01"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write(csv_content)
        temp_path = f.name

    try:
        df = load_kpi_csv(temp_path)
        assert len(df) == 3
        assert "timestamp" in df.columns
        assert all(col in df.columns for col in FEATURES)
        assert pd.api.types.is_datetime64_any_dtype(df["timestamp"])
    finally:
        os.unlink(temp_path)
