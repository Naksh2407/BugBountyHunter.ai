import uuid

from sqlalchemy import Column
from sqlalchemy import String

from app.core.database import Base


class Repository(Base):
    __tablename__ = "repositories"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    github_url = Column(String, nullable=False)

    repo_name = Column(String, nullable=False)

    status = Column(String, default="pending")