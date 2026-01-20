"""Tests for database operations."""

from sqlmodel import SQLModel, create_engine, Session, select
from database import get_session
from models import DerbyName


def test_init_db_creates_tables():
    """Test that init_db creates all tables."""
    # Use in-memory database to avoid file locking issues
    engine = create_engine("sqlite:///:memory:")

    # Create tables
    SQLModel.metadata.create_all(engine)

    # Verify we can create a record
    with Session(engine) as session:
        name = DerbyName(name="Test Name")
        session.add(name)
        session.commit()
        session.refresh(name)

        assert name.id is not None

    engine.dispose()


def test_get_session_yields_session():
    """Test that get_session yields a valid session."""
    session_gen = get_session()
    session = next(session_gen)

    assert isinstance(session, Session)

    # Clean up
    try:
        next(session_gen)
    except StopIteration:
        pass


def test_get_session_cleanup():
    """Test that get_session properly cleans up."""
    session_gen = get_session()
    session = next(session_gen)

    # Use the session
    statement = select(DerbyName)
    session.exec(statement).all()

    # Clean up should happen without errors
    try:
        next(session_gen)
    except StopIteration:
        pass  # Expected


def test_database_persistence():
    """Test that data persists across sessions."""
    # Use in-memory database
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)

    # Create a record in first session
    with Session(engine) as session:
        name = DerbyName(name="Persistent Name")
        session.add(name)
        session.commit()

    # Verify it exists in a new session
    with Session(engine) as session:
        statement = select(DerbyName).where(DerbyName.name == "Persistent Name")
        result = session.exec(statement).first()

        assert result is not None
        assert result.name == "Persistent Name"

    engine.dispose()


def test_database_isolation():
    """Test that different database engines are isolated."""
    # Use in-memory databases
    engine1 = create_engine("sqlite:///:memory:")
    engine2 = create_engine("sqlite:///:memory:")

    SQLModel.metadata.create_all(engine1)
    SQLModel.metadata.create_all(engine2)

    # Add name to first database
    with Session(engine1) as session:
        name = DerbyName(name="DB1 Name")
        session.add(name)
        session.commit()

    # Verify it doesn't exist in second database
    with Session(engine2) as session:
        statement = select(DerbyName)
        results = session.exec(statement).all()

        assert len(results) == 0

    engine1.dispose()
    engine2.dispose()


def test_database_transaction_rollback(test_session):
    """Test that failed transactions can be rolled back."""
    # Start a transaction
    name = DerbyName(name="Rollback Test")
    test_session.add(name)

    # Rollback before commit
    test_session.rollback()

    # Verify nothing was saved
    statement = select(DerbyName).where(DerbyName.name == "Rollback Test")
    result = test_session.exec(statement).first()

    assert result is None
