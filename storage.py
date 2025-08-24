from sqlmodel import SQLModel, Field, create_engine, Session
from datetime import datetime

# Use SQLite database
engine = create_engine("sqlite:///netops.db", echo=False)


class Upload(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    filename: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Score(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    upload_id: int
    cell_id: str
    ts: str
    anomaly: int
    score: float
    # Original KPI data for AI analysis
    prb_util: float | None = Field(default=None)
    rrc_conn: float | None = Field(default=None)
    throughput_mbps: float | None = Field(default=None)
    bler: float | None = Field(default=None)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    return Session(engine)


def close_session(session):
    """Close database session"""
    if session:
        session.close()
