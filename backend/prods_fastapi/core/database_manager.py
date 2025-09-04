"""
Centralized Database Connection Manager
Eliminates duplicate database connection patterns across the application
"""
import os
import logging
from typing import Optional, Dict, Any, AsyncGenerator, Generator
from contextlib import asynccontextmanager, contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import QueuePool
import threading
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class DatabaseConfig:
    """Database configuration settings"""
    url: str
    async_url: Optional[str] = None
    pool_size: int = 20
    max_overflow: int = 30
    pool_timeout: int = 30
    pool_recycle: int = 3600
    pool_pre_ping: bool = True
    echo: bool = False
    future: bool = True
    
    def __post_init__(self):
        if not self.async_url:
            self.async_url = self.url.replace('postgresql://', 'postgresql+asyncpg://')

@dataclass
class ConnectionStats:
    """Database connection statistics"""
    total_connections: int = 0
    active_connections: int = 0
    total_queries: int = 0
    failed_connections: int = 0
    avg_query_time: float = 0.0
    last_connection_time: Optional[datetime] = None
    connection_errors: Dict[str, int] = field(default_factory=dict)

class DatabaseConnectionManager:
    """
    Centralized database connection manager
    Eliminates duplicate connection patterns across the application
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, config: Optional[DatabaseConfig] = None):
        """Singleton pattern to ensure single connection manager"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, config: Optional[DatabaseConfig] = None):
        if hasattr(self, '_initialized'):
            return
        
        # Set up default configuration if none provided
        if config is None:
            database_url = os.getenv(
                "DATABASE_URL", 
                "postgresql://localhost:5432/ai_fashion_dev"
            )
            config = DatabaseConfig(url=database_url)
        
        self.config = config
        self.stats = ConnectionStats()
        
        # Initialize engines
        self._sync_engine = None
        self._async_engine = None
        self._sync_session_maker = None
        self._async_session_maker = None
        
        self._initialized = True
        logger.info(f"Database connection manager initialized with URL: {config.url.split('@')[0] + '@***'}")
    
    @property
    def sync_engine(self):
        """Get or create sync engine"""
        if self._sync_engine is None:
            self._sync_engine = create_engine(
                self.config.url,
                poolclass=QueuePool,
                pool_size=self.config.pool_size,
                max_overflow=self.config.max_overflow,
                pool_timeout=self.config.pool_timeout,
                pool_recycle=self.config.pool_recycle,
                pool_pre_ping=self.config.pool_pre_ping,
                echo=self.config.echo,
                future=self.config.future
            )
            logger.info("Sync database engine created")
        return self._sync_engine
    
    @property
    def async_engine(self):
        """Get or create async engine"""
        if self._async_engine is None:
            self._async_engine = create_async_engine(
                self.config.async_url,
                poolclass=QueuePool,
                pool_size=self.config.pool_size,
                max_overflow=self.config.max_overflow,
                pool_timeout=self.config.pool_timeout,
                pool_recycle=self.config.pool_recycle,
                pool_pre_ping=self.config.pool_pre_ping,
                echo=self.config.echo,
                future=self.config.future
            )
            logger.info("Async database engine created")
        return self._async_engine
    
    @property
    def sync_session_maker(self):
        """Get or create sync session maker"""
        if self._sync_session_maker is None:
            self._sync_session_maker = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.sync_engine
            )
        return self._sync_session_maker
    
    @property
    def async_session_maker(self):
        """Get or create async session maker"""
        if self._async_session_maker is None:
            self._async_session_maker = async_sessionmaker(
                bind=self.async_engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
        return self._async_session_maker
    
    @contextmanager
    def get_sync_session(self) -> Generator[Session, None, None]:
        """
        Get sync database session with automatic cleanup
        
        Usage:
            with db_manager.get_sync_session() as session:
                result = session.query(Model).all()
        """
        session = self.sync_session_maker()
        start_time = datetime.utcnow()
        
        try:
            self.stats.total_connections += 1
            self.stats.last_connection_time = start_time
            
            yield session
            session.commit()
            
        except Exception as e:
            session.rollback()
            self.stats.failed_connections += 1
            error_type = type(e).__name__
            self.stats.connection_errors[error_type] = self.stats.connection_errors.get(error_type, 0) + 1
            logger.error(f"Sync database session error: {e}")
            raise
            
        finally:
            session.close()
            
            # Update stats
            duration = (datetime.utcnow() - start_time).total_seconds()
            self.stats.total_queries += 1
            self.stats.avg_query_time = (
                (self.stats.avg_query_time * (self.stats.total_queries - 1) + duration) / 
                self.stats.total_queries
            )
    
    @asynccontextmanager
    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get async database session with automatic cleanup
        
        Usage:
            async with db_manager.get_async_session() as session:
                result = await session.execute(select(Model))
        """
        session = self.async_session_maker()
        start_time = datetime.utcnow()
        
        try:
            self.stats.total_connections += 1
            self.stats.last_connection_time = start_time
            
            yield session
            await session.commit()
            
        except Exception as e:
            await session.rollback()
            self.stats.failed_connections += 1
            error_type = type(e).__name__
            self.stats.connection_errors[error_type] = self.stats.connection_errors.get(error_type, 0) + 1
            logger.error(f"Async database session error: {e}")
            raise
            
        finally:
            await session.close()
            
            # Update stats
            duration = (datetime.utcnow() - start_time).total_seconds()
            self.stats.total_queries += 1
            self.stats.avg_query_time = (
                (self.stats.avg_query_time * (self.stats.total_queries - 1) + duration) / 
                self.stats.total_queries
            )
    
    def execute_raw_query(self, query: str, params: Optional[Dict] = None) -> Any:
        """
        Execute raw SQL query with sync engine
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            Query result
        """
        with self.get_sync_session() as session:
            result = session.execute(text(query), params or {})
            return result.fetchall()
    
    async def execute_raw_query_async(self, query: str, params: Optional[Dict] = None) -> Any:
        """
        Execute raw SQL query with async engine
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            Query result
        """
        async with self.get_async_session() as session:
            result = await session.execute(text(query), params or {})
            return result.fetchall()
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform sync database health check
        
        Returns:
            Health check results
        """
        try:
            start_time = datetime.utcnow()
            
            with self.get_sync_session() as session:
                result = session.execute(text("SELECT 1"))
                result.fetchone()
            
            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return {
                "status": "healthy",
                "response_time_ms": round(response_time, 2),
                "connection_stats": self.get_connection_stats()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "connection_stats": self.get_connection_stats()
            }
    
    async def health_check_async(self) -> Dict[str, Any]:
        """
        Perform async database health check
        
        Returns:
            Health check results
        """
        try:
            start_time = datetime.utcnow()
            
            async with self.get_async_session() as session:
                result = await session.execute(text("SELECT 1"))
                result.fetchone()
            
            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return {
                "status": "healthy",
                "response_time_ms": round(response_time, 2),
                "connection_stats": self.get_connection_stats()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "connection_stats": self.get_connection_stats()
            }
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """
        Get current connection statistics
        
        Returns:
            Connection statistics dictionary
        """
        pool_stats = {}
        
        try:
            sync_pool = self.sync_engine.pool
            pool_stats.update({
                "sync_pool_size": sync_pool.size(),
                "sync_checked_out": sync_pool.checkedout(),
                "sync_overflow": sync_pool.overflow(),
                "sync_checked_in": sync_pool.checkedin()
            })
        except Exception as e:
            pool_stats["sync_pool_error"] = str(e)
        
        try:
            if self._async_engine:
                async_pool = self.async_engine.pool
                pool_stats.update({
                    "async_pool_size": async_pool.size(),
                    "async_checked_out": async_pool.checkedout(),
                    "async_overflow": async_pool.overflow(),
                    "async_checked_in": async_pool.checkedin()
                })
        except Exception as e:
            pool_stats["async_pool_error"] = str(e)
        
        return {
            "total_connections": self.stats.total_connections,
            "failed_connections": self.stats.failed_connections,
            "total_queries": self.stats.total_queries,
            "avg_query_time_seconds": round(self.stats.avg_query_time, 4),
            "last_connection_time": self.stats.last_connection_time.isoformat() if self.stats.last_connection_time else None,
            "connection_errors": dict(self.stats.connection_errors),
            "pool_stats": pool_stats
        }
    
    def close(self):
        """Close all database connections"""
        if self._sync_engine:
            self._sync_engine.dispose()
            logger.info("Sync database engine disposed")
        
        if self._async_engine:
            # Note: async engine disposal should be done with await
            logger.info("Async database engine marked for disposal")
    
    async def close_async(self):
        """Close all async database connections"""
        if self._async_engine:
            await self._async_engine.dispose()
            logger.info("Async database engine disposed")

# Global database manager instance
db_manager: Optional[DatabaseConnectionManager] = None

def get_database_manager(config: Optional[DatabaseConfig] = None) -> DatabaseConnectionManager:
    """
    Get the global database manager instance
    
    Args:
        config: Optional database configuration
        
    Returns:
        Database manager instance
    """
    global db_manager
    if db_manager is None:
        db_manager = DatabaseConnectionManager(config)
    return db_manager

def initialize_database_manager(config: Optional[DatabaseConfig] = None):
    """
    Initialize the global database manager
    
    Args:
        config: Optional database configuration
    """
    global db_manager
    db_manager = DatabaseConnectionManager(config)
    logger.info("Global database manager initialized")

# Convenience functions for backward compatibility
def get_sync_session():
    """Get sync database session (backward compatibility)"""
    return get_database_manager().get_sync_session()

def get_async_session():
    """Get async database session (backward compatibility)"""
    return get_database_manager().get_async_session()

def get_sync_engine():
    """Get sync database engine"""
    return get_database_manager().sync_engine

def get_async_engine():
    """Get async database engine"""
    return get_database_manager().async_engine

# FastAPI dependency functions
def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for sync database session"""
    with get_database_manager().get_sync_session() as session:
        yield session

async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for async database session"""
    async with get_database_manager().get_async_session() as session:
        yield session
