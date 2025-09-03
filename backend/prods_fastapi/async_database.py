"""
Async Database Operations for AI Fashion Backend
Provides async database access with connection pooling and caching.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import selectinload
from sqlalchemy import select, and_, or_
from sqlalchemy.pool import NullPool
import os
from cache_manager import cache_manager, async_cached

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://fashion_jvy9_user:0d2Nn5mvyw6KMBDT21l9olpHaxrTPEzh@dpg-d1vhvpbuibrs739dkn3g-a.oregon-postgres.render.com/fashion_jvy9"
)

# Log the database URL being used (without sensitive info)
logger.info(f"Using database URL: {DATABASE_URL.split('@')[0] + '@***'}")

# Convert to async URL
ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Global variables for lazy initialization
async_engine = None
AsyncSessionLocal = None

def _initialize_async_engine():
    """Lazy initialization of async database engine"""
    global async_engine, AsyncSessionLocal
    
    if async_engine is None:
        try:
            # Create async engine with connection pooling
            async_engine = create_async_engine(
                ASYNC_DATABASE_URL,
                echo=False,
                future=True,
                pool_size=20,
                max_overflow=30,
                pool_timeout=30,
                pool_recycle=3600,
                pool_pre_ping=True
            )
            
            # Create async session factory
            AsyncSessionLocal = async_sessionmaker(
                bind=async_engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            logger.info("Async database engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize async database engine: {e}")
            # Set dummy values to prevent repeated initialization attempts
            async_engine = "unavailable"
            AsyncSessionLocal = None
    
    return async_engine, AsyncSessionLocal

class AsyncDatabaseService:
    """Async database service with caching and connection pooling"""
    
    def __init__(self):
        self.engine = None
        self.session_factory = None
        self._initialized = False
    
    def _ensure_initialized(self):
        """Ensure database engine is initialized"""
        if not self._initialized:
            self.engine, self.session_factory = _initialize_async_engine()
            self._initialized = True
    
    async def get_session(self) -> AsyncSession:
        """Get async database session"""
        self._ensure_initialized()
        if not self.session_factory:
            raise RuntimeError("Database not available")
        return self.session_factory()
    
    @async_cached(expire_seconds=7200, key_prefix="color_palettes")
    async def get_color_palettes(self, skin_tone: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get color palettes from database with caching
        
        Args:
            skin_tone: Optional skin tone filter
            
        Returns:
            List of color palette dictionaries
        """
        try:
            async with self.session_factory() as session:
                from database import ColorPalette
                
                query = select(ColorPalette)
                if skin_tone:
                    query = query.where(ColorPalette.skin_tone == skin_tone)
                
                result = await session.execute(query)
                palettes = result.scalars().all()
                
                return [
                    {
                        "id": palette.id,
                        "skin_tone": palette.skin_tone,
                        "flattering_colors": palette.flattering_colors,
                        "colors_to_avoid": palette.colors_to_avoid,
                        "description": palette.description
                    }
                    for palette in palettes
                ]
                
        except Exception as e:
            logger.error(f"Error getting color palettes: {e}")
            return []
    
    @async_cached(expire_seconds=7200, key_prefix="skin_tone_mappings")
    async def get_skin_tone_mappings(self, monk_tone: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get skin tone mappings from database with caching
        
        Args:
            monk_tone: Optional monk tone filter
            
        Returns:
            List of skin tone mapping dictionaries
        """
        try:
            async with self.session_factory() as session:
                from database import SkinToneMapping
                
                query = select(SkinToneMapping)
                if monk_tone:
                    query = query.where(SkinToneMapping.monk_tone == monk_tone)
                
                result = await session.execute(query)
                mappings = result.scalars().all()
                
                return [
                    {
                        "id": mapping.id,
                        "monk_tone": mapping.monk_tone,
                        "seasonal_type": mapping.seasonal_type,
                        "hex_code": mapping.hex_code
                    }
                    for mapping in mappings
                ]
                
        except Exception as e:
            logger.error(f"Error getting skin tone mappings: {e}")
            return []
    
    @async_cached(expire_seconds=3600, key_prefix="color_hex_data")
    async def get_color_hex_data(self, seasonal_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get color hex data from database with caching
        
        Args:
            seasonal_type: Optional seasonal type filter
            
        Returns:
            List of color hex data dictionaries
        """
        try:
            async with self.session_factory() as session:
                from database import ColorHexData
                
                query = select(ColorHexData)
                if seasonal_type:
                    query = query.where(ColorHexData.seasonal_type == seasonal_type)
                
                result = await session.execute(query)
                hex_data = result.scalars().all()
                
                return [
                    {
                        "id": data.id,
                        "seasonal_type": data.seasonal_type,
                        "hex_codes": data.hex_codes,
                        "data_source": data.data_source
                    }
                    for data in hex_data
                ]
                
        except Exception as e:
            logger.error(f"Error getting color hex data: {e}")
            return []
    
    @async_cached(expire_seconds=3600, key_prefix="color_suggestions")
    async def get_color_suggestions(self, skin_tone: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get color suggestions from database with caching
        
        Args:
            skin_tone: Optional skin tone filter
            
        Returns:
            List of color suggestion dictionaries
        """
        try:
            async with self.session_factory() as session:
                from database import ColorSuggestions
                
                query = select(ColorSuggestions)
                if skin_tone:
                    query = query.where(ColorSuggestions.skin_tone == skin_tone)
                
                result = await session.execute(query)
                suggestions = result.scalars().all()
                
                return [
                    {
                        "id": suggestion.id,
                        "skin_tone": suggestion.skin_tone,
                        "suitable_colors_text": suggestion.suitable_colors_text,
                        "data_source": suggestion.data_source
                    }
                    for suggestion in suggestions
                ]
                
        except Exception as e:
            logger.error(f"Error getting color suggestions: {e}")
            return []
    
    async def create_color_palette(self, palette_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a new color palette in database
        
        Args:
            palette_data: Color palette data dictionary
            
        Returns:
            Created palette dictionary or None if failed
        """
        try:
            async with self.session_factory() as session:
                from database import ColorPalette
                
                palette = ColorPalette(
                    skin_tone=palette_data["skin_tone"],
                    flattering_colors=palette_data["flattering_colors"],
                    colors_to_avoid=palette_data.get("colors_to_avoid", []),
                    description=palette_data.get("description", "")
                )
                
                session.add(palette)
                await session.commit()
                await session.refresh(palette)
                
                # Invalidate cache
                cache_manager.flush_pattern("color_palettes:*")
                
                return {
                    "id": palette.id,
                    "skin_tone": palette.skin_tone,
                    "flattering_colors": palette.flattering_colors,
                    "colors_to_avoid": palette.colors_to_avoid,
                    "description": palette.description
                }
                
        except Exception as e:
            logger.error(f"Error creating color palette: {e}")
            return None
    
    async def update_color_palette(self, palette_id: int, palette_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update an existing color palette in database
        
        Args:
            palette_id: ID of palette to update
            palette_data: Updated palette data dictionary
            
        Returns:
            Updated palette dictionary or None if failed
        """
        try:
            async with self.session_factory() as session:
                from database import ColorPalette
                
                query = select(ColorPalette).where(ColorPalette.id == palette_id)
                result = await session.execute(query)
                palette = result.scalar_one_or_none()
                
                if not palette:
                    return None
                
                # Update fields
                if "skin_tone" in palette_data:
                    palette.skin_tone = palette_data["skin_tone"]
                if "flattering_colors" in palette_data:
                    palette.flattering_colors = palette_data["flattering_colors"]
                if "colors_to_avoid" in palette_data:
                    palette.colors_to_avoid = palette_data["colors_to_avoid"]
                if "description" in palette_data:
                    palette.description = palette_data["description"]
                
                await session.commit()
                await session.refresh(palette)
                
                # Invalidate cache
                cache_manager.flush_pattern("color_palettes:*")
                
                return {
                    "id": palette.id,
                    "skin_tone": palette.skin_tone,
                    "flattering_colors": palette.flattering_colors,
                    "colors_to_avoid": palette.colors_to_avoid,
                    "description": palette.description
                }
                
        except Exception as e:
            logger.error(f"Error updating color palette: {e}")
            return None
    
    async def delete_color_palette(self, palette_id: int) -> bool:
        """
        Delete a color palette from database
        
        Args:
            palette_id: ID of palette to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            async with self.session_factory() as session:
                from database import ColorPalette
                
                query = select(ColorPalette).where(ColorPalette.id == palette_id)
                result = await session.execute(query)
                palette = result.scalar_one_or_none()
                
                if not palette:
                    return False
                
                await session.delete(palette)
                await session.commit()
                
                # Invalidate cache
                cache_manager.flush_pattern("color_palettes:*")
                
                return True
                
        except Exception as e:
            logger.error(f"Error deleting color palette: {e}")
            return False
    
    async def bulk_create_color_palettes(self, palettes_data: List[Dict[str, Any]]) -> int:
        """
        Bulk create color palettes in database
        
        Args:
            palettes_data: List of color palette data dictionaries
            
        Returns:
            Number of palettes created successfully
        """
        try:
            async with self.session_factory() as session:
                from database import ColorPalette
                
                palettes = []
                for palette_data in palettes_data:
                    palette = ColorPalette(
                        skin_tone=palette_data["skin_tone"],
                        flattering_colors=palette_data["flattering_colors"],
                        colors_to_avoid=palette_data.get("colors_to_avoid", []),
                        description=palette_data.get("description", "")
                    )
                    palettes.append(palette)
                
                session.add_all(palettes)
                await session.commit()
                
                # Invalidate cache
                cache_manager.flush_pattern("color_palettes:*")
                
                return len(palettes)
                
        except Exception as e:
            logger.error(f"Error bulk creating color palettes: {e}")
            return 0
    
    async def search_palettes_by_colors(self, color_names: List[str]) -> List[Dict[str, Any]]:
        """
        Search color palettes that contain specific colors
        
        Args:
            color_names: List of color names to search for
            
        Returns:
            List of matching color palette dictionaries
        """
        try:
            async with self.session_factory() as session:
                from database import ColorPalette
                import json
                
                # This is a simplified search - in production you might want to use full-text search
                query = select(ColorPalette)
                result = await session.execute(query)
                all_palettes = result.scalars().all()
                
                matching_palettes = []
                for palette in all_palettes:
                    # Check if any of the requested colors are in the palette
                    flattering_colors = palette.flattering_colors or []
                    palette_color_names = [color.get("name", "").lower() for color in flattering_colors]
                    
                    for color_name in color_names:
                        if any(color_name.lower() in palette_name for palette_name in palette_color_names):
                            matching_palettes.append({
                                "id": palette.id,
                                "skin_tone": palette.skin_tone,
                                "flattering_colors": palette.flattering_colors,
                                "colors_to_avoid": palette.colors_to_avoid,
                                "description": palette.description
                            })
                            break
                
                return matching_palettes
                
        except Exception as e:
            logger.error(f"Error searching palettes by colors: {e}")
            return []
    
    async def get_database_stats(self) -> Dict[str, Any]:
        """
        Get database statistics
        
        Returns:
            Dictionary with database statistics
        """
        try:
            async with self.session_factory() as session:
                from database import ColorPalette, SkinToneMapping, ColorHexData, ColorSuggestions
                
                # Count records in each table
                color_palettes_count = await session.execute(select(ColorPalette).count())
                skin_tone_mappings_count = await session.execute(select(SkinToneMapping).count())
                color_hex_data_count = await session.execute(select(ColorHexData).count())
                color_suggestions_count = await session.execute(select(ColorSuggestions).count())
                
                return {
                    "color_palettes": color_palettes_count.scalar(),
                    "skin_tone_mappings": skin_tone_mappings_count.scalar(),
                    "color_hex_data": color_hex_data_count.scalar(),
                    "color_suggestions": color_suggestions_count.scalar(),
                    "connection_pool_size": self.engine.pool.size(),
                    "checked_out_connections": self.engine.pool.checkedout()
                }
                
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {
                "error": str(e),
                "color_palettes": 0,
                "skin_tone_mappings": 0,
                "color_hex_data": 0,
                "color_suggestions": 0
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform database health check
        
        Returns:
            Dictionary with health check results
        """
        try:
            async with self.session_factory() as session:
                # Simple query to test connection
                result = await session.execute(select(1))
                result.scalar()
                
                return {
                    "status": "healthy",
                    "message": "Database connection is working",
                    "connection_pool_size": self.engine.pool.size(),
                    "checked_out_connections": self.engine.pool.checkedout()
                }
                
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "message": "Database connection failed"
            }
    
    async def close(self):
        """Close database connections"""
        try:
            await self.engine.dispose()
            logger.info("Database connections closed")
        except Exception as e:
            logger.error(f"Error closing database connections: {e}")

# Initialize database tables asynchronously
async def async_create_tables():
    """Create database tables asynchronously"""
    try:
        # Ensure async_db_service is initialized
        async_db_service._ensure_initialized()
        
        # Check if engine is available
        if not async_db_service.engine or async_db_service.engine == "unavailable":
            logger.error("Database engine not available, skipping table creation")
            return
        
        from database import Base
        async with async_db_service.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Async database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating async database tables: {e}")
        # Don't raise the exception to allow the app to start without DB

# Global async database service instance
async_db_service = AsyncDatabaseService()

# Dependency for FastAPI
async def get_async_db() -> AsyncSession:
    """Dependency to get async database session"""
    async with async_db_service.session_factory() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()


# Initialize color palette data asynchronously
async def async_init_color_palette_data():
    """Initialize color palette data asynchronously"""
    try:
        # Check if data already exists
        palettes = await async_db_service.get_color_palettes()
        if palettes:
            logger.info(f"Color palette data already exists ({len(palettes)} records)")
            return
        
        # Import initial data
        from database import init_color_palette_data
        
        # Run sync function in executor
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, init_color_palette_data)
        
        logger.info("Async color palette data initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing async color palette data: {e}")

# Cache warming functions
async def warm_async_caches():
    """Warm up async caches with frequently accessed data"""
    try:
        logger.info("Warming async caches")
        
        # Pre-load popular skin tone data
        popular_skin_tones = ["Clear Winter", "Warm Spring", "Deep Autumn", "Light Spring"]
        for skin_tone in popular_skin_tones:
            await async_db_service.get_color_palettes(skin_tone)
            await async_db_service.get_color_hex_data(skin_tone)
            await async_db_service.get_color_suggestions(skin_tone)
        
        # Pre-load monk tone mappings
        popular_monk_tones = ["Monk01", "Monk03", "Monk05", "Monk07", "Monk10"]
        for monk_tone in popular_monk_tones:
            await async_db_service.get_skin_tone_mappings(monk_tone)
        
        logger.info("Async caches warmed successfully")
        
    except Exception as e:
        logger.error(f"Error warming async caches: {e}")

# Connection pool monitoring
async def monitor_connection_pool():
    """Monitor database connection pool health"""
    try:
        stats = await async_db_service.get_database_stats()
        
        pool_size = stats.get("connection_pool_size", 0)
        checked_out = stats.get("checked_out_connections", 0)
        
        if checked_out > pool_size * 0.8:  # 80% utilization warning
            logger.warning(f"High database connection pool utilization: {checked_out}/{pool_size}")
        
        return {
            "pool_size": pool_size,
            "checked_out_connections": checked_out,
            "utilization_percent": (checked_out / pool_size * 100) if pool_size > 0 else 0
        }
        
    except Exception as e:
        logger.error(f"Error monitoring connection pool: {e}")
        return {"error": str(e)}
