import uuid

from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Text

from app.core.database import Base


class Fix(Base):
    __tablename__ = "fixes"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    scan_id = Column(String)

    file_path = Column(String)

    patch = Column(Text)

    status = Column(String)