# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from database import Base
from routers import candidates, vacancies, interviews, search
import os

# Create a synchronous engine for the initial table creation
# This is a simple approach for development. For production, use Alembic migrations.
DATABASE_URL_SYNC = os.getenv("DATABASE_URL", "").replace("asyncpg", "psycopg2")
if DATABASE_URL_SYNC:
    engine_sync = create_engine(DATABASE_URL_SYNC)
    Base.metadata.create_all(bind=engine_sync)

app = FastAPI(
    title="HR Application Backend",
    description="API for managing candidates, vacancies, and interviews with LLM integration.",
    version="1.0.0"
)

# CORS (Cross-Origin Resource Sharing)
# This allows your frontend (on a different domain) to communicate with this backend.
origins = [
    "http://localhost",
    "http://localhost:3000", # Example for a React frontend
    # Add your deployed frontend URL here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all the routers
app.include_router(search.router)
app.include_router(candidates.router)
app.include_router(vacancies.router)
app.include_router(interviews.router)

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the HR Application API!"}