from features import load_kpi_csv, to_matrix
from model import load_model, score
from storage import get_session, Score
import sys

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python batch_score.py <kpi_csv_file>")
        sys.exit(1)

    df = load_kpi_csv(sys.argv[1])
    X = to_matrix(df)
    m = load_model()
    if m is None:
        print("model missing. run batch_train first.")
        exit(1)
    pred, sc = score(m, X)
    with get_session() as s:
        for (cell, ts), a, r in zip(
            df[["cell_id", "timestamp"]].itertuples(index=False, name=None), pred, sc
        ):
            s.add(
                Score(
                    upload_id=0,
                    cell_id=str(cell),
                    ts=str(ts),
                    anomaly=int(a),
                    score=float(r),
                )
            )
        s.commit()
    print("scored:", len(pred))
