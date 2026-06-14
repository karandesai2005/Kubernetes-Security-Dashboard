"""Database engine, session, and init helpers (async SQLAlchemy)."""
from __future__ import annotations
import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings
from app.models.base import Base

# Import all models so metadata is populated
from app.models import threat, vulnerability, rbac  # noqa: F401

logger = logging.getLogger(__name__)

engine: AsyncEngine | None = None
async_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    global engine
    if engine is None:
        connect_args = {}
        if "sqlite" in settings.database_url:
            connect_args = {"check_same_thread": False}
        engine = create_async_engine(
            settings.database_url,
            echo=False,
            pool_pre_ping=True,
            connect_args=connect_args,
        )
    return engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    global async_session_factory
    if async_session_factory is None:
        async_session_factory = async_sessionmaker(
            bind=get_engine(),
            expire_on_commit=False,
        )
    return async_session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for a request-scoped async DB session."""
    factory = get_session_factory()
    async with factory() as session:
        yield session


@asynccontextmanager
async def get_db_context() -> AsyncGenerator[AsyncSession, None]:
    """Context manager for scripts / background tasks."""
    factory = get_session_factory()
    async with factory() as session:
        yield session


async def init_db(create_tables: bool = True) -> None:
    """Initialize DB: optionally create tables (dev convenience)."""
    eng = get_engine()
    if create_tables:
        async with eng.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created (or already exist)")


async def close_db() -> None:
    global engine
    if engine is not None:
        await engine.dispose()
        engine = None
        logger.info("Database engine disposed")