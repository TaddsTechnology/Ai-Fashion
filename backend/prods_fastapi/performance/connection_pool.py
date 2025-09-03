"""
Database Connection Pool Manager with Performance Monitoring
"""
import os
import time
import asyncio
import logging
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import QueuePool
from sqlalchemy import event, create_engine
from dataclasses import dataclass
import threading
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class PoolStats:
    """Database connection pool statistics"""
    total_connections: int = 0
    active_connections: int = 0
    idle_connections: int = 0
    checked_out_connections: int = 0
    overflow_connections: int = 0
    total_checkouts: int = 0
    total_checkins: int = 0
    connection_errors: int = 0
    avg_checkout_time: float = 0.0
    max_checkout_time: float = 0.0

class DatabaseConnectionPool:
    """Enhanced database connection pool with monitoring"""
    
    def __init__(self):
        self.stats = PoolStats()
        self.checkout_times = []
        self._lock = threading.Lock()
        
        # Get database URL from environment
        database_url = os.getenv(
            "DATABASE_URL", 
            "postgresql://localhost:5432/ai_fashion_dev"
        )
        
        # Convert to async URL if needed
        if database_url.startswith('postgresql://'):
            async_database_url = database_url.replace('postgresql://', 'postgresql+asyncpg://')
        else:
            async_database_url = database_url
            
        # Create async engine with connection pooling
        self.async_engine = create_async_engine(
            async_database_url,
            poolclass=QueuePool,
            pool_size=20,  # Base connections
            max_overflow=30,  # Additional connections when needed
            pool_pre_ping=True,  # Verify connections before use
            pool_recycle=3600,  # Recycle connections after 1 hour
            pool_timeout=30,  # Timeout for getting connection from pool
            echo=False,  # Set to True for SQL debugging
            future=True
        )
        
        # Create sync engine for legacy operations
        sync_database_url = database_url
        if sync_database_url.startswith('postgresql+asyncpg://'):
            sync_database_url = sync_database_url.replace('postgresql+asyncpg://', 'postgresql://')
            
        self.sync_engine = create_engine(
            sync_database_url,
            poolclass=QueuePool,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=3600,
            pool_timeout=30,
            echo=False
        )
        
        # Create session makers
        self.async_session_maker = async_sessionmaker(
            self.async_engine, 
            class_=AsyncSession, 
            expire_on_commit=False
        )
        
        # Set up connection pool monitoring
        self._setup_pool_monitoring()
        
    def _setup_pool_monitoring(self):
        """Set up database connection pool monitoring"""
        
        @event.listens_for(self.async_engine.sync_engine, "connect")
        def on_connect(dbapi_connection, connection_record):
            with self._lock:
                self.stats.total_connections += 1
                logger.debug("New database connection created")
                
        @event.listens_for(self.async_engine.sync_engine, "checkout")
        def on_checkout(dbapi_connection, connection_record, connection_proxy):
            connection_record.checkout_time = time.time()
            with self._lock:
                self.stats.total_checkouts += 1
                self.stats.checked_out_connections += 1
                
        @event.listens_for(self.async_engine.sync_engine, "checkin")
        def on_checkin(dbapi_connection, connection_record):
            checkout_time = getattr(connection_record, 'checkout_time', None)
            if checkout_time:
                duration = time.time() - checkout_time
                with self._lock:
                    self.checkout_times.append(duration)
                    if len(self.checkout_times) > 1000:  # Keep last 1000 measurements
                        self.checkout_times = self.checkout_times[-500:]
                    
                    self.stats.total_checkins += 1
                    self.stats.checked_out_connections = max(0, self.stats.checked_out_connections - 1)
                    self.stats.avg_checkout_time = sum(self.checkout_times) / len(self.checkout_times)
                    self.stats.max_checkout_time = max(self.checkout_times)
                    
        # Set up sync engine monitoring too
        @event.listens_for(self.sync_engine, "connect")
        def on_sync_connect(dbapi_connection, connection_record):
            logger.debug("New sync database connection created")
                    
    def get_pool_stats(self) -> Dict[str, Any]:
        """Get current connection pool statistics"""
        pool = self.async_engine.pool
        
        with self._lock:
            self.stats.active_connections = pool.checkedout()
            self.stats.idle_connections = pool.checkedin()
            self.stats.overflow_connections = pool.overflow()
            
            return {
                "total_connections": self.stats.total_connections,
                "active_connections": self.stats.active_connections,
                "idle_connections": self.stats.idle_connections,
                "checked_out_connections": self.stats.checked_out_connections,
                "overflow_connections": self.stats.overflow_connections,
                "total_checkouts": self.stats.total_checkouts,
                "total_checkins": self.stats.total_checkins,
                "connection_errors": self.stats.connection_errors,
                "avg_checkout_time_ms": round(self.stats.avg_checkout_time * 1000, 2),
                "max_checkout_time_ms": round(self.stats.max_checkout_time * 1000, 2),
                "pool_size": pool.size(),
                "pool_capacity": pool.size() + pool.overflow(),
            }
    
    @asynccontextmanager
    async def get_async_session(self):
        """Get async database session with automatic cleanup"""
        session = self.async_session_maker()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
    
    def get_sync_session(self):
        """Get sync database session (legacy support)"""
        from sqlalchemy.orm import sessionmaker
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.sync_engine)
        return SessionLocal()
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform database health check"""
        start_time = time.time()
        try:
            async with self.get_async_session() as session:
                result = await session.execute("SELECT 1")
                result.fetchone()
                
            response_time = (time.time() - start_time) * 1000
            
            return {
                "status": "healthy",
                "response_time_ms": round(response_time, 2),
                "pool_stats": self.get_pool_stats()
            }
        except Exception as e:
            with self._lock:
                self.stats.connection_errors += 1
            return {
                "status": "unhealthy",
                "error": str(e),
                "response_time_ms": round((time.time() - start_time) * 1000, 2),
                "pool_stats": self.get_pool_stats()
            }
    
    async def close(self):
        """Close all database connections"""
        await self.async_engine.dispose()
        self.sync_engine.dispose()
        logger.info("Database connection pool closed")

# Global connection pool instance
db_pool: Optional[DatabaseConnectionPool] = None

def get_db_pool() -> DatabaseConnectionPool:
    """Get or create database connection pool"""
    global db_pool
    if db_pool is None:
        db_pool = DatabaseConnectionPool()
        logger.info("Database connection pool initialized")
    return db_pool

async def init_db_pool():
    """Initialize database connection pool"""
    global db_pool
    if db_pool is None:
        db_pool = DatabaseConnectionPool()
        logger.info("Async database connection pool initialized")
    return db_pool

async def close_db_pool():
    """Close database connection pool"""
    global db_pool
    if db_pool:
        await db_pool.close()
        db_pool = None
        logger.info("Database connection pool closed")
