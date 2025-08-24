from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from storage import init_db, get_session, Upload, Score
from features import load_kpi_csv, to_matrix
from model import load_model, train, score
from charts import save_kpi_chart
from summarize import extract_incidents
import tempfile
import os

app = FastAPI(
    title="NetOps AI Pipeline",
    description="KPI anomaly detection and log summarization",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()


@app.get("/health")
def health():
    return {"status": "ok", "service": "netops-ai-pipeline"}


@app.post("/upload")
async def upload(file: UploadFile = File(...), train_if_missing: bool = Form(True)):
    """Upload KPI CSV file for anomaly detection"""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
    tmp.write(await file.read())
    tmp.close()

    up_id = None
    with get_session() as s:
        u = Upload(filename=file.filename)
        s.add(u)
        s.commit()
        s.refresh(u)
        up_id = u.id

    try:
        df = load_kpi_csv(tmp.name)
        X = to_matrix(df)
        m = load_model()
        if m is None and train_if_missing:
            m = train(X)
        elif m is None:
            return JSONResponse(
                {"error": "model missing; set train_if_missing=true"}, status_code=400
            )

        pred, sc = score(m, X)
        df_out = df.copy()
        df_out["anomaly"] = pred
        df_out["score"] = sc

        chart_path = tempfile.NamedTemporaryFile(delete=False, suffix=".png").name
        save_kpi_chart(df_out, chart_path)

        with get_session() as s:
            for row in df_out[["cell_id", "timestamp", "anomaly", "score"]].itertuples(
                index=False, name=None
            ):
                s.add(
                    Score(
                        upload_id=up_id,
                        cell_id=str(row[0]),
                        ts=str(row[1]),
                        anomaly=int(row[2]),
                        score=float(row[3]),
                    )
                )
            s.commit()

        return {
            "upload_id": up_id,
            "filename": file.filename,
            "total_samples": len(df_out),
            "summary": df_out["anomaly"].value_counts().to_dict(),
            "chart": chart_path,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")
    finally:
        os.unlink(tmp.name)


@app.get("/report/{upload_id}")
def report(upload_id: int):
    """Get anomaly detection report for an upload"""
    with get_session() as s:
        rows = s.query(Score).filter(Score.upload_id == upload_id).all()
    if not rows:
        raise HTTPException(status_code=404, detail="Upload not found")

    anomalies = sum(1 for r in rows if r.anomaly == -1)
    return {
        "upload_id": upload_id,
        "total": len(rows),
        "anomalies": anomalies,
        "anomaly_rate": round(anomalies / len(rows) * 100, 2) if rows else 0,
    }


@app.get("/chart/{upload_id}")
def get_chart(upload_id: int):
    """Get visualization chart for an upload"""
    return {"message": "Chart endpoint - implementation needed"}


@app.post("/logs/summarize")
async def summarize_logs(file: UploadFile = File(...)):
    """Summarize syslog incidents using GenAI"""
    if not file.filename.endswith((".log", ".txt")):
        raise HTTPException(status_code=400, detail="Only log/txt files are supported")

    content = await file.read()
    log_text = content.decode("utf-8")

    incidents = extract_incidents(log_text)

    return {
        "filename": file.filename,
        "summary": incidents["summary"],
        "incident_counts": incidents["incident_counts"],
        "analysis": "Log analysis complete - GenAI integration available with API key",
    }


@app.get("/uploads")
def list_uploads():
    """List all uploads"""
    with get_session() as s:
        uploads = s.query(Upload).all()
    return [
        {"id": u.id, "filename": u.filename, "created_at": u.created_at}
        for u in uploads
    ]
