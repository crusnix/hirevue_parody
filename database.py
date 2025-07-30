# database.py
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

# Load environment variables from .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# The async engine for database operations
engine = create_async_engine(DATABASE_URL)

# The async session maker
async_session_local = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# The base class for our ORM models
Base = declarative_base()

# Dependency to get a DB session in our API endpoints
async def get_db():
    async with async_session_local() as session:
        yield session