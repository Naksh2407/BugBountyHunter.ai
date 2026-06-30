from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.exc import OperationalError

from app.core.config import settings

# Attempt PostgreSQL connection, fallback to SQLite if offline
try:
    engine = create_engine(settings.DATABASE_URL)
    # Test connection
    with engine.connect() as conn:
        pass
except (OperationalError, Exception):
    print("PostgreSQL database connection failed. Falling back to local SQLite database.")
    # SQLite fallback, check_same_thread allowed for multiple concurrent worker contexts
    engine = create_engine(
        "sqlite:///./autofix.db",
        connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()