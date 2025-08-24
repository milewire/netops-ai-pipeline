from storage import Upload, get_session
from pathlib import Path


def register_upload(path: str) -> int:
    with get_session() as s:
        u = Upload(filename=Path(path).name)
        s.add(u)
        s.commit()
        s.refresh(u)
        return u.id
