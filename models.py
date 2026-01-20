from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, Column
from sqlalchemy.types import JSON, DateTime


class DerbyName(SQLModel, table=True):
    """Database model for storing roller derby names."""

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=datetime.utcnow)
    )
    is_favorite: bool = Field(default=False)
    meta: Optional[dict] = Field(default_factory=dict, sa_column=Column(JSON))


class DerbyNameCreate(SQLModel):
    """Schema for creating a new derby name."""

    name: str


class DerbyNameResponse(SQLModel):
    """Schema for derby name API responses."""

    id: int
    name: str
    created_at: datetime
    is_favorite: bool
    meta: Optional[dict]
