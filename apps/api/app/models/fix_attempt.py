import uuid

from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy import Text
from sqlalchemy import Float

from app.core.database import Base


class FixAttempt(Base):
    __tablename__ = "fix_attempts"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    scan_id = Column(String, nullable=False)

    file_path = Column(String, nullable=False)

    line_number = Column(Integer, nullable=True)

    original_code = Column(Text, nullable=True)

    candidate_code = Column(Text, nullable=True)

    patch = Column(Text, nullable=True)

    score = Column(Float, default=0.0)

    validation_result = Column(Text, nullable=True)

    status = Column(String, default="pending")
