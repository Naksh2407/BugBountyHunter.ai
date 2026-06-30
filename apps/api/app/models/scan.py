import uuid

from sqlalchemy import Column, String, JSON, Integer, Float, Text

from app.core.database import Base


class Scan(Base):
    __tablename__ = "scans"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    repository_id = Column(String)

    findings = Column(JSON)

    status = Column(String)

    # Added for Kaggle Capstone Course Metrics & Observability
    token_usage = Column(Integer, default=0, nullable=True)
    
    execution_time = Column(Float, default=0.0, nullable=True)
    
    reasoning_trace = Column(Text, default="", nullable=True)