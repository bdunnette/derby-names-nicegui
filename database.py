from sqlmodel import SQLModel, create_engine, Session
from pathlib import Path

# Create database directory if it doesn't exist
DB_DIR = Path(__file__).parent / "data"
DB_DIR.mkdir(exist_ok=True)

# SQLite database URL
DATABASE_URL = f"sqlite:///{DB_DIR}/derby_names.db"

# Create engine with SQLite-specific settings
engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},  # Required for SQLite with FastAPI
)


def init_db():
    """Initialize the database and create all tables."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Get a database session."""
    with Session(engine) as session:
        yield session
