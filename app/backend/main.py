from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import os
import time

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://todo:todo@db:5432/tododb")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Model ---

class TodoItem(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    completed = Column(Boolean, default=False)
    priority = Column(String, default="medium")  # low | medium | high
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# --- Schemas ---

class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Optional[str] = "medium"

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[str] = None

class TodoResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    completed: bool
    priority: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- DB Dependency ---

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- App ---

app = FastAPI(title="Todo API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Wait for DB + Create tables ---

def init_db(retries=10, delay=2):
    for i in range(retries):
        try:
            Base.metadata.create_all(bind=engine)
            print("Database ready.")
            return
        except Exception as e:
            print(f"DB not ready ({i+1}/{retries}): {e}")
            time.sleep(delay)
    raise RuntimeError("Could not connect to database")

@app.on_event("startup")
def startup():
    init_db()

# --- Routes ---

@app.get("/health")
def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

@app.get("/todos", response_model=list[TodoResponse])
def list_todos(completed: Optional[bool] = None, priority: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(TodoItem)
    if completed is not None:
        q = q.filter(TodoItem.completed == completed)
    if priority:
        q = q.filter(TodoItem.priority == priority)
    return q.order_by(TodoItem.created_at.desc()).all()

@app.post("/todos", response_model=TodoResponse, status_code=201)
def create_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    item = TodoItem(**todo.dict())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@app.get("/todos/{todo_id}", response_model=TodoResponse)
def get_todo(todo_id: int, db: Session = Depends(get_db)):
    item = db.query(TodoItem).filter(TodoItem.id == todo_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Todo not found")
    return item

@app.patch("/todos/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, update: TodoUpdate, db: Session = Depends(get_db)):
    item = db.query(TodoItem).filter(TodoItem.id == todo_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Todo not found")
    for field, value in update.dict(exclude_unset=True).items():
        setattr(item, field, value)
    item.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(item)
    return item

@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    item = db.query(TodoItem).filter(TodoItem.id == todo_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(item)
    db.commit()

@app.get("/stats")
def stats(db: Session = Depends(get_db)):
    total = db.query(TodoItem).count()
    completed = db.query(TodoItem).filter(TodoItem.completed == True).count()
    by_priority = {
        "high": db.query(TodoItem).filter(TodoItem.priority == "high").count(),
        "medium": db.query(TodoItem).filter(TodoItem.priority == "medium").count(),
        "low": db.query(TodoItem).filter(TodoItem.priority == "low").count(),
    }
    return {
        "total": total,
        "completed": completed,
        "pending": total - completed,
        "by_priority": by_priority,
    }
