from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from typing import List
import asyncio

from models import DerbyName, DerbyNameCreate, DerbyNameResponse
from database import get_session, init_db
from generator import get_generator

# Create FastAPI app
app = FastAPI(title="Derby Name Generator API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Background task flag
background_task_running = False


async def generate_names_background():
    """Background task to generate names periodically."""
    global background_task_running
    background_task_running = True

    print("Background name generation task started")

    while background_task_running:
        try:
            # Wait 60 seconds between generations
            await asyncio.sleep(60)

            # Generate a new name
            generator = get_generator()
            name = generator.generate()

            # Save to database
            from database import engine

            with Session(engine) as session:
                db_name = DerbyName(name=name)
                session.add(db_name)
                session.commit()
                print(f"Background task generated: {name}")
        except Exception as e:
            print(f"Error in background task: {e}")


@app.on_event("startup")
async def on_startup():
    """Initialize database and start background task on startup."""
    init_db()
    # Start background task
    asyncio.create_task(generate_names_background())
    print("API started with background name generation")


@app.on_event("shutdown")
async def on_shutdown():
    """Stop background task on shutdown."""
    global background_task_running
    background_task_running = False
    print("Background task stopped")


@app.post("/api/generate", response_model=DerbyNameResponse)
def generate_name(session: Session = Depends(get_session)):
    """Generate a new derby name using Markovify."""
    generator = get_generator()
    name = generator.generate()

    # Save to database
    db_name = DerbyName(name=name)
    session.add(db_name)
    session.commit()
    session.refresh(db_name)

    return db_name


@app.get("/api/names", response_model=List[DerbyNameResponse])
def get_names(session: Session = Depends(get_session)):
    """Get all saved derby names."""
    statement = select(DerbyName).order_by(DerbyName.created_at.desc())
    names = session.exec(statement).all()
    return names


@app.post("/api/names", response_model=DerbyNameResponse)
def create_name(name_data: DerbyNameCreate, session: Session = Depends(get_session)):
    """Save a custom derby name."""
    db_name = DerbyName(name=name_data.name)
    session.add(db_name)
    session.commit()
    session.refresh(db_name)
    return db_name


@app.delete("/api/names/{name_id}")
def delete_name(name_id: int, session: Session = Depends(get_session)):
    """Delete a derby name."""
    statement = select(DerbyName).where(DerbyName.id == name_id)
    name = session.exec(statement).first()
    if not name:
        raise HTTPException(status_code=404, detail="Name not found")

    session.delete(name)
    session.commit()
    return {"message": "Name deleted successfully"}


@app.patch("/api/names/{name_id}/favorite", response_model=DerbyNameResponse)
def toggle_favorite(name_id: int, session: Session = Depends(get_session)):
    """Toggle favorite status of a derby name."""
    statement = select(DerbyName).where(DerbyName.id == name_id)
    name = session.exec(statement).first()
    if not name:
        raise HTTPException(status_code=404, detail="Name not found")

    name.is_favorite = not name.is_favorite
    session.add(name)
    session.commit()
    session.refresh(name)
    return name
