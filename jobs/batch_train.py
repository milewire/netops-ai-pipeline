from features import load_kpi_csv, to_matrix
from model import train
import sys

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python batch_train.py <kpi_csv_file>")
        sys.exit(1)

    df = load_kpi_csv(sys.argv[1])
    X = to_matrix(df)
    train(X)
    print("trained:", len(X))
