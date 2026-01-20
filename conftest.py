"""Pytest configuration and shared fixtures."""

import pytest
from sqlmodel import SQLModel, create_engine, Session
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from pathlib import Path
import tempfile


@pytest.fixture(name="test_engine")
def test_engine_fixture():
    """Create an in-memory SQLite engine for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture(name="test_session")
def test_session_fixture(test_engine):
    """Create a database session for testing."""
    with Session(test_engine) as session:
        yield session


@pytest.fixture(name="mock_generator")
def mock_generator_fixture():
    """Create a mocked DerbyNameGenerator."""
    mock = Mock()
    mock.generate.return_value = "Test Derby Name"
    return mock


@pytest.fixture(name="test_client")
def test_client_fixture(mock_generator):
    """Create a FastAPI TestClient with test database and mocked generator."""
    from api import app
    from database import get_session

    # Create a separate test engine with tables
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    SQLModel.metadata.create_all(test_engine)

    # Override the database session dependency
    def override_get_session():
        with Session(test_engine) as session:
            yield session

    # Disable startup/shutdown events during testing
    app.router.on_startup = []
    app.router.on_shutdown = []

    app.dependency_overrides[get_session] = override_get_session

    # Mock the generator to avoid downloading/training during tests
    with patch("api.get_generator", return_value=mock_generator):
        with TestClient(app) as client:
            yield client

    # Clean up
    app.dependency_overrides.clear()
    test_engine.dispose()


@pytest.fixture(name="temp_data_dir")
def temp_data_dir_fixture():
    """Create a temporary directory for test data files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture(name="sample_derby_names")
def sample_derby_names_fixture():
    """Provide sample derby names for testing."""
    return """Roller Girl
Skate or Die
Derby Queen
Thunder Thighs
Bruise Almighty
Smack That
Pain Train
Demolition Dolly
Slam Bam
Whiplash"""
