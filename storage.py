from sqlmodel import SQLModel, Field, create_engine, Session
from datetime import datetime

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


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    return Session(engine)
