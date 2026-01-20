"""Tests for SQLModel models."""

import pytest
from datetime import datetime
from sqlmodel import select
from models import DerbyName, DerbyNameCreate, DerbyNameResponse


def test_derby_name_creation(test_session):
    """Test creating a DerbyName instance."""
    name = DerbyName(name="Test Derby Name")
    test_session.add(name)
    test_session.commit()
    test_session.refresh(name)

    assert name.id is not None
    assert name.name == "Test Derby Name"
    assert isinstance(name.created_at, datetime)
    assert name.is_favorite is False


def test_derby_name_defaults(test_session):
    """Test default values for DerbyName fields."""
    name = DerbyName(name="Default Test")

    # Before saving
    assert name.id is None
    assert name.is_favorite is False

    test_session.add(name)
    test_session.commit()
    test_session.refresh(name)

    # After saving
    assert name.id is not None
    assert isinstance(name.created_at, datetime)


def test_derby_name_unique_constraint(test_session):
    """Test that duplicate names are not allowed."""
    name1 = DerbyName(name="Unique Name")
    test_session.add(name1)
    test_session.commit()

    # Try to add duplicate
    name2 = DerbyName(name="Unique Name")
    test_session.add(name2)

    with pytest.raises(Exception):  # SQLite will raise IntegrityError
        test_session.commit()


def test_derby_name_favorite_toggle(test_session):
    """Test toggling favorite status."""
    name = DerbyName(name="Favorite Test")
    test_session.add(name)
    test_session.commit()
    test_session.refresh(name)

    assert name.is_favorite is False

    # Toggle to true
    name.is_favorite = True
    test_session.add(name)
    test_session.commit()
    test_session.refresh(name)

    assert name.is_favorite is True

    # Toggle back to false
    name.is_favorite = False
    test_session.add(name)
    test_session.commit()
    test_session.refresh(name)

    assert name.is_favorite is False


def test_derby_name_create_schema():
    """Test DerbyNameCreate schema validation."""
    create_data = DerbyNameCreate(name="Schema Test")
    assert create_data.name == "Schema Test"


def test_derby_name_response_schema(test_session):
    """Test DerbyNameResponse schema serialization."""
    name = DerbyName(name="Response Test")
    test_session.add(name)
    test_session.commit()
    test_session.refresh(name)

    response = DerbyNameResponse(
        id=name.id,
        name=name.name,
        created_at=name.created_at,
        is_favorite=name.is_favorite,
    )

    assert response.id == name.id
    assert response.name == "Response Test"
    assert isinstance(response.created_at, datetime)
    assert response.is_favorite is False


def test_query_names_ordered_by_created_at(test_session):
    """Test querying names ordered by creation date."""
    # Create multiple names
    names = [
        DerbyName(name="First"),
        DerbyName(name="Second"),
        DerbyName(name="Third"),
    ]

    for name in names:
        test_session.add(name)
        test_session.commit()

    # Query ordered by created_at descending
    statement = select(DerbyName).order_by(DerbyName.created_at.desc())
    results = test_session.exec(statement).all()

    assert len(results) == 3
    assert results[0].name == "Third"
    assert results[1].name == "Second"
    assert results[2].name == "First"
