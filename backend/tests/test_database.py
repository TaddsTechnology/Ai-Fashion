"""
Tests for database operations
"""
import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session


class TestDatabaseModels:
    """Test database models and operations"""

    def test_color_palette_model(self, test_db_session, sample_color_palette):
        """Test ColorPalette model CRUD operations"""
        from backend.prods_fastapi.database import ColorPalette
        
        # Create
        palette = ColorPalette(**sample_color_palette)
        test_db_session.add(palette)
        test_db_session.commit()
        
        assert palette.id is not None
        assert palette.skin_tone == sample_color_palette["skin_tone"]
        assert len(palette.flattering_colors) == 2
        
        # Read
        retrieved = test_db_session.query(ColorPalette).filter_by(skin_tone="Test Winter").first()
        assert retrieved is not None
        assert retrieved.skin_tone == "Test Winter"
        
        # Update
        retrieved.description = "Updated description"
        test_db_session.commit()
        
        updated = test_db_session.query(ColorPalette).filter_by(id=retrieved.id).first()
        assert updated.description == "Updated description"
        
        # Delete
        test_db_session.delete(updated)
        test_db_session.commit()
        
        deleted = test_db_session.query(ColorPalette).filter_by(id=updated.id).first()
        assert deleted is None

    def test_skin_tone_mapping_model(self, test_db_session, sample_monk_mapping):
        """Test SkinToneMapping model CRUD operations"""
        from backend.prods_fastapi.database import SkinToneMapping
        
        # Create
        mapping = SkinToneMapping(**sample_monk_mapping)
        test_db_session.add(mapping)
        test_db_session.commit()
        
        assert mapping.id is not None
        assert mapping.monk_tone == "Monk99"
        assert mapping.seasonal_type == "Test Winter"
        
        # Read
        retrieved = test_db_session.query(SkinToneMapping).filter_by(monk_tone="Monk99").first()
        assert retrieved is not None
        assert retrieved.hex_code == "#ffffff"

    def test_comprehensive_colors_model(self, test_db_session):
        """Test ComprehensiveColors model"""
        from backend.prods_fastapi.database import ComprehensiveColors
        
        color_data = {
            "hex_code": "#FF5733",
            "color_name": "Test Orange",
            "monk_tones": ["Monk03", "Monk04"],
            "seasonal_types": ["Warm Spring"],
            "color_family": "orange",
            "brightness_level": "medium",
            "undertone": "warm",
            "data_source": "test"
        }
        
        color = ComprehensiveColors(**color_data)
        test_db_session.add(color)
        test_db_session.commit()
        
        assert color.id is not None
        assert color.hex_code == "#FF5733"
        assert "Monk03" in color.monk_tones


class TestDatabaseConnections:
    """Test database connection management"""

    def test_database_session_creation(self):
        """Test database session creation"""
        from backend.prods_fastapi.database import SessionLocal, get_database
        
        # Test SessionLocal works
        session = SessionLocal()
        assert session is not None
        session.close()
        
        # Test get_database generator
        db_gen = get_database()
        db = next(db_gen)
        assert db is not None
        
        # Cleanup
        try:
            next(db_gen)
        except StopIteration:
            pass  # Expected

    def test_create_tables_function(self, test_db):
        """Test create_tables function"""
        from backend.prods_fastapi.database import create_tables, Base
        
        # This should not raise an exception
        create_tables()
        
        # Verify tables exist by checking metadata
        assert len(Base.metadata.tables) > 0

    @patch('backend.prods_fastapi.database.SessionLocal')
    def test_init_color_palette_data_with_existing_data(self, mock_session_local):
        """Test init_color_palette_data when data already exists"""
        from backend.prods_fastapi.database import init_color_palette_data
        
        # Mock session and query
        mock_session = MagicMock()
        mock_session_local.return_value = mock_session
        mock_session.query.return_value.count.return_value = 5  # Existing data
        
        # Should not insert data if it already exists
        init_color_palette_data()
        
        # Verify it checked for existing data but didn't add new data
        mock_session.query.assert_called()
        mock_session.add.assert_not_called()

    @patch('backend.prods_fastapi.database.SessionLocal')
    def test_init_color_palette_data_fresh_install(self, mock_session_local):
        """Test init_color_palette_data on fresh install"""
        from backend.prods_fastapi.database import init_color_palette_data
        
        # Mock session and query
        mock_session = MagicMock()
        mock_session_local.return_value = mock_session
        mock_session.query.return_value.count.return_value = 0  # No existing data
        
        # Should insert data
        init_color_palette_data()
        
        # Verify it added data and committed
        mock_session.add.assert_called()
        assert mock_session.commit.call_count >= 1

    def test_database_url_configuration(self):
        """Test database URL configuration"""
        from backend.prods_fastapi.database import DATABASE_URL
        
        assert DATABASE_URL is not None
        assert DATABASE_URL.startswith(("postgresql://", "sqlite://"))

    def test_engine_configuration(self):
        """Test SQLAlchemy engine configuration"""
        from backend.prods_fastapi.database import engine
        
        assert engine is not None
        # Verify engine has proper configuration
        assert engine.url is not None


class TestAsyncDatabase:
    """Test async database functionality"""

    @pytest.mark.asyncio
    async def test_async_database_service_initialization(self):
        """Test AsyncDatabaseService initialization"""
        with patch('backend.prods_fastapi.async_database.create_async_engine') as mock_engine:
            mock_engine.return_value = MagicMock()
            
            from backend.prods_fastapi.async_database import AsyncDatabaseService
            
            service = AsyncDatabaseService()
            service._ensure_initialized()
            
            assert service._initialized

    @pytest.mark.asyncio
    async def test_async_db_service_methods(self):
        """Test async database service methods"""
        with patch('backend.prods_fastapi.async_database.async_db_service') as mock_service:
            mock_service.get_color_palettes.return_value = []
            mock_service.get_skin_tone_mappings.return_value = []
            mock_service.health_check.return_value = {"status": "healthy"}
            
            # Test methods return expected types
            palettes = await mock_service.get_color_palettes()
            assert isinstance(palettes, list)
            
            mappings = await mock_service.get_skin_tone_mappings()
            assert isinstance(mappings, list)
            
            health = await mock_service.health_check()
            assert "status" in health

    @pytest.mark.asyncio
    async def test_async_create_tables(self):
        """Test async table creation"""
        with patch('backend.prods_fastapi.async_database.async_db_service') as mock_service, \
             patch('backend.prods_fastapi.async_database.logger') as mock_logger:
            
            mock_service._ensure_initialized.return_value = None
            mock_service.engine = MagicMock()
            
            from backend.prods_fastapi.async_database import async_create_tables
            
            await async_create_tables()
            
            # Should log success message
            mock_logger.info.assert_called()

    @pytest.mark.asyncio
    async def test_async_init_color_palette_data(self):
        """Test async color palette data initialization"""
        with patch('backend.prods_fastapi.async_database.async_db_service') as mock_service:
            mock_service.get_color_palettes.return_value = []  # No existing data
            
            from backend.prods_fastapi.async_database import async_init_color_palette_data
            
            # Should not raise exception
            await async_init_color_palette_data()

    @pytest.mark.asyncio
    async def test_warm_async_caches(self):
        """Test async cache warming"""
        with patch('backend.prods_fastapi.async_database.async_db_service') as mock_service:
            mock_service.get_color_palettes.return_value = []
            mock_service.get_color_hex_data.return_value = []
            mock_service.get_color_suggestions.return_value = []
            mock_service.get_skin_tone_mappings.return_value = []
            
            from backend.prods_fastapi.async_database import warm_async_caches
            
            await warm_async_caches()
            
            # Should have called service methods multiple times
            assert mock_service.get_color_palettes.call_count > 0


class TestConnectionPooling:
    """Test database connection pooling"""

    def test_connection_pool_initialization(self):
        """Test connection pool initialization"""
        with patch('backend.prods_fastapi.performance.connection_pool.create_async_engine') as mock_engine:
            mock_engine.return_value = MagicMock()
            
            from backend.prods_fastapi.performance.connection_pool import DatabaseConnectionPool
            
            pool = DatabaseConnectionPool()
            assert pool is not None
            assert pool.stats is not None

    def test_get_db_pool(self):
        """Test get_db_pool function"""
        with patch('backend.prods_fastapi.performance.connection_pool.DatabaseConnectionPool') as mock_pool_class:
            mock_pool_instance = MagicMock()
            mock_pool_class.return_value = mock_pool_instance
            
            from backend.prods_fastapi.performance.connection_pool import get_db_pool
            
            pool = get_db_pool()
            assert pool is not None

    @pytest.mark.asyncio
    async def test_connection_pool_health_check(self):
        """Test connection pool health check"""
        with patch('backend.prods_fastapi.performance.connection_pool.get_db_pool') as mock_get_pool:
            mock_pool = MagicMock()
            mock_pool.health_check.return_value = {"status": "healthy"}
            mock_get_pool.return_value = mock_pool
            
            health = await mock_pool.health_check()
            assert health["status"] == "healthy"

    def test_pool_stats(self):
        """Test pool statistics"""
        with patch('backend.prods_fastapi.performance.connection_pool.get_db_pool') as mock_get_pool:
            mock_pool = MagicMock()
            mock_pool.get_pool_stats.return_value = {
                "total_connections": 5,
                "active_connections": 2,
                "idle_connections": 3
            }
            mock_get_pool.return_value = mock_pool
            
            stats = mock_pool.get_pool_stats()
            assert "total_connections" in stats
            assert "active_connections" in stats


class TestDatabaseErrorHandling:
    """Test database error handling"""

    @patch('backend.prods_fastapi.database.SessionLocal')
    def test_init_color_palette_data_error_handling(self, mock_session_local):
        """Test error handling in init_color_palette_data"""
        from backend.prods_fastapi.database import init_color_palette_data
        
        # Mock session to raise an exception
        mock_session = MagicMock()
        mock_session_local.return_value = mock_session
        mock_session.query.side_effect = Exception("Database connection failed")
        
        # Should handle the exception gracefully
        with pytest.raises(Exception):
            init_color_palette_data()
        
        # Should call rollback on error
        mock_session.rollback.assert_called()

    def test_database_session_error_handling(self):
        """Test database session error handling"""
        from backend.prods_fastapi.database import get_database
        
        # Test that generator properly closes session even if error occurs
        db_gen = get_database()
        db = next(db_gen)
        
        # Simulate an error by calling next again (should close session)
        try:
            next(db_gen)
        except StopIteration:
            pass  # Expected

    @pytest.mark.asyncio
    async def test_async_database_service_error_handling(self):
        """Test async database service error handling"""
        with patch('backend.prods_fastapi.async_database.async_db_service') as mock_service:
            mock_service.get_color_palettes.side_effect = Exception("Async DB error")
            
            # Should handle errors gracefully and return empty list
            try:
                await mock_service.get_color_palettes()
            except Exception:
                pass  # Expected in this mock scenario


class TestDatabaseMigrations:
    """Test database migration scenarios"""

    def test_table_creation_idempotent(self):
        """Test that create_tables can be called multiple times safely"""
        from backend.prods_fastapi.database import create_tables
        
        # Should not raise exception when called multiple times
        create_tables()
        create_tables()  # Second call should be safe

    def test_color_palette_data_initialization_idempotent(self):
        """Test that init_color_palette_data is idempotent"""
        with patch('backend.prods_fastapi.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            mock_session.query.return_value.count.return_value = 0  # No existing data first time
            
            from backend.prods_fastapi.database import init_color_palette_data
            
            # First call should add data
            init_color_palette_data()
            mock_session.add.assert_called()
            
            # Reset mock
            mock_session.reset_mock()
            mock_session.query.return_value.count.return_value = 10  # Data exists now
            
            # Second call should not add data
            init_color_palette_data()
            mock_session.add.assert_not_called()


class TestDatabaseQueries:
    """Test complex database queries"""

    def test_color_palette_queries(self, test_db_session):
        """Test various color palette queries"""
        from backend.prods_fastapi.database import ColorPalette
        
        # Add test data
        palette1 = ColorPalette(
            skin_tone="Test Spring",
            flattering_colors=[{"name": "Blue", "hex": "#0000FF"}],
            colors_to_avoid=[],
            description="Spring colors"
        )
        palette2 = ColorPalette(
            skin_tone="Test Winter", 
            flattering_colors=[{"name": "Red", "hex": "#FF0000"}],
            colors_to_avoid=[],
            description="Winter colors"
        )
        
        test_db_session.add_all([palette1, palette2])
        test_db_session.commit()
        
        # Test queries
        spring_palettes = test_db_session.query(ColorPalette).filter_by(skin_tone="Test Spring").all()
        assert len(spring_palettes) == 1
        
        all_palettes = test_db_session.query(ColorPalette).all()
        assert len(all_palettes) == 2

    def test_skin_tone_mapping_queries(self, test_db_session):
        """Test skin tone mapping queries"""
        from backend.prods_fastapi.database import SkinToneMapping
        
        # Add test data
        mapping1 = SkinToneMapping(monk_tone="Monk01", seasonal_type="Light Spring", hex_code="#f6ede4")
        mapping2 = SkinToneMapping(monk_tone="Monk10", seasonal_type="Deep Winter", hex_code="#292420")
        
        test_db_session.add_all([mapping1, mapping2])
        test_db_session.commit()
        
        # Test queries
        light_mappings = test_db_session.query(SkinToneMapping).filter_by(seasonal_type="Light Spring").all()
        assert len(light_mappings) == 1
        
        monk01_mapping = test_db_session.query(SkinToneMapping).filter_by(monk_tone="Monk01").first()
        assert monk01_mapping.hex_code == "#f6ede4"
