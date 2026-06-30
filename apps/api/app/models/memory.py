import uuid

from sqlalchemy import Column, String, Text

from app.core.database import Base


class FixPatternMemory(Base):
    __tablename__ = "fix_pattern_memories"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    tool = Column(String, nullable=False)            # e.g., "ruff", "mypy", "bandit", "eslint"
    error_type = Column(String, nullable=False)      # e.g., "F821" (Ruff undefined var), "B101" (Bandit assert)
    file_extension = Column(String, nullable=False)  # e.g., ".py", ".js", ".ts"
    error_context = Column(Text, nullable=True)     # key error message lines / regex match
    successful_patch = Column(Text, nullable=False)  # replacement patch content
