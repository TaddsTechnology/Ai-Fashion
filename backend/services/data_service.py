"""
Data service module for AI-Fashion backend.

This module centralizes data loading, processing, and caching operations,
providing a clean interface for the main application.
"""

import pandas as pd
import json
import os
import logging
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_validation import DataLoader, DataValidationError
from prods_fastapi.color_utils import get_color_mapping, get_seasonal_palettes, get_monk_hex_codes

logger = logging.getLogger(__name__)


class DataService:
    """
    Service class for managing all data operations including loading, 
    validation, caching, and processing.
    """
    
    def __init__(self, data_dir: str = None, cache_dir: str = "cache"):
        """
        Initialize data service with data directory and caching.
        
        Args:
            data_dir: Directory containing data files
            cache_dir: Directory for caching processed data
        """
        self.data_dir = Path(data_dir) if data_dir else Path("../processed_data")
        self.cache_dir = Path(cache_dir)
        self.data_loader = DataLoader(cache_dir)
        
        # Initialize data containers
        self._color_mapping = None
        self._seasonal_palettes = None
        self._monk_hex_codes = None
        self._datasets = {}
        
        # Load initial data
        self._load_initial_data()
    
    def _load_initial_data(self):
        """Load initial data and configurations."""
        try:
            # Load color data
            self._color_mapping = get_color_mapping()
            self._seasonal_palettes = get_seasonal_palettes()
            self._monk_hex_codes = get_monk_hex_codes()
            
            # Add default Monk skin tone hex codes if not loaded
            if not self._monk_hex_codes:
                self._monk_hex_codes = {
                    "Monk01": ["#f6ede4"],
                    "Monk02": ["#f3e7db"],
                    "Monk03": ["#f7ead0"],
                    "Monk04": ["#eadaba"],
                    "Monk05": ["#d7bd96"],
                    "Monk06": ["#a07e56"],
                    "Monk07": ["#825c43"],
                    "Monk08": ["#604134"],
                    "Monk09": ["#3a312a"],
                    "Monk10": ["#292420"]
                }
            
            logger.info("Successfully loaded initial data configurations")
            
        except Exception as e:
            logger.error(f"Error loading initial data: {str(e)}")
            # Set defaults
            self._color_mapping = {}
            self._seasonal_palettes = {}
            self._monk_hex_codes = {}
    
    def get_color_mapping(self) -> Dict[str, str]:
        """Get color mapping dictionary."""
        return self._color_mapping or {}
    
    def get_seasonal_palettes(self) -> Dict[str, Any]:
        """Get seasonal palettes dictionary."""
        return self._seasonal_palettes or {}
    
    def get_monk_hex_codes(self) -> Dict[str, List[str]]:
        """Get Monk skin tone hex codes dictionary."""
        return self._monk_hex_codes or {}
    
    def load_hm_products(self, use_cache: bool = True) -> pd.DataFrame:
        """
        Load H&M products data with validation and caching.
        
        Args:
            use_cache: Whether to use cached data if available
            
        Returns:
            pd.DataFrame: H&M products data
        """
        cache_key = "hm_products"
        
        # Try to load from cache first
        if use_cache:
            cached_data = self.data_loader.load_from_cache(cache_key)
            if cached_data is not None:
                logger.info("Loaded H&M products from cache")
                return cached_data
        
        # Load from files
        try:
            df = self.data_loader.load_csv_with_fallback(
                primary_path=str(self.data_dir / "hm_products_hm_products.csv"),
                fallback_paths=[
                    "hm_products2.csv",
                    "hm_products.csv"
                ],
                required_columns=["Product Name"],
                default_df=pd.DataFrame(columns=[
                    "Product Name", "Price", "Image URL", "Product Type", 
                    "brand", "gender", "baseColour", "masterCategory", "subCategory"
                ])
            )
            
            # Cache the data
            if use_cache and not df.empty:
                self.data_loader.cache_data(df, cache_key)
            
            logger.info(f"Successfully loaded H&M products ({len(df)} records)")
            return df
            
        except Exception as e:
            logger.error(f"Error loading H&M products: {str(e)}")
            return pd.DataFrame()
    
    def load_makeup_products(self, use_cache: bool = True) -> pd.DataFrame:
        """
        Load makeup products data with validation and caching.
        
        Args:
            use_cache: Whether to use cached data if available
            
        Returns:
            pd.DataFrame: Makeup products data
        """
        cache_key = "makeup_products"
        
        # Try to load from cache first
        if use_cache:
            cached_data = self.data_loader.load_from_cache(cache_key)
            if cached_data is not None:
                logger.info("Loaded makeup products from cache")
                return cached_data
        
        # Load from files
        try:
            df = self.data_loader.load_csv_with_fallback(
                primary_path=str(self.data_dir / "sample_makeup_products.csv"),
                fallback_paths=[
                    str(self.data_dir / "all_makeup_products.csv"),
                    "processed_data/all_makeup_products.csv",
                    "ulta_with_mst_index.csv",
                    "ulta_sephora_with_mst_index.csv"
                ],
                required_columns=["product"],
                default_df=pd.DataFrame(columns=[
                    "product", "brand", "price", "imgSrc", "mst", "hex", "desc", "product_type"
                ])
            )
            
            # Cache the data
            if use_cache and not df.empty:
                self.data_loader.cache_data(df, cache_key)
            
            logger.info(f"Successfully loaded makeup products ({len(df)} records)")
            return df
            
        except Exception as e:
            logger.error(f"Error loading makeup products: {str(e)}")
            return pd.DataFrame()
    
    def load_outfit_products(self, use_cache: bool = True) -> pd.DataFrame:
        """
        Load outfit products data with validation and caching.
        
        Args:
            use_cache: Whether to use cached data if available
            
        Returns:
            pd.DataFrame: Outfit products data
        """
        cache_key = "outfit_products"
        
        # Try to load from cache first
        if use_cache:
            cached_data = self.data_loader.load_from_cache(cache_key)
            if cached_data is not None:
                logger.info("Loaded outfit products from cache")
                return cached_data
        
        # Load from files and combine
        try:
            outfit_products = []
            
        # Load outfit1 data (commented out - coming soon feature)
        # df_outfit1 = self.data_loader.load_csv_with_fallback(
        #     primary_path=str(self.data_dir / "outfit_products_outfit1.csv"),
        #     fallback_paths=["outfit_products_outfit1.csv"],
        #     default_df=pd.DataFrame()
        # )
        df_outfit1 = pd.DataFrame()  # Placeholder for coming soon feature
            
            if not df_outfit1.empty and 'products' in df_outfit1.columns:
                try:
                    products_str = df_outfit1.iloc[0]['products']
                    if isinstance(products_str, str):
                        import ast
                        outfit_products.extend(ast.literal_eval(products_str))
                except (ValueError, SyntaxError, IndexError) as e:
                    logger.warning(f"Error parsing outfit1 products: {e}")
            
            # Load outfit2 data
            df_outfit2 = self.data_loader.load_csv_with_fallback(
                primary_path=str(self.data_dir / "outfit_products_outfit2.csv"),
                fallback_paths=["outfit_products_outfit2.csv"],
                default_df=pd.DataFrame()
            )
            
            if not df_outfit2.empty and 'products' in df_outfit2.columns:
                try:
                    products_str = df_outfit2.iloc[0]['products']
                    if isinstance(products_str, str):
                        import ast
                        outfit_products.extend(ast.literal_eval(products_str))
                except (ValueError, SyntaxError, IndexError) as e:
                    logger.warning(f"Error parsing outfit2 products: {e}")
            
            # Load apparel data as fallback
            df_apparel = self.data_loader.load_csv_with_fallback(
                primary_path="processed_data/outfit_products.csv",
                fallback_paths=["apparel.csv"],
                default_df=pd.DataFrame()
            )
            
            if not df_apparel.empty:
                for _, row in df_apparel.iterrows():
                    outfit_products.append({
                        'brand': row.get('brand', 'Fashion Brand'),
                        'price': row.get('Price', ''),
                        'images': row.get('Image URL', ''),
                        'product_name': row.get('Product Name', ''),
                        'gender': row.get('gender', ''),
                        'baseColour': row.get('baseColour', ''),
                        'masterCategory': row.get('masterCategory', ''),
                        'subCategory': row.get('subCategory', '')
                    })
            
            # Convert to DataFrame
            df = pd.DataFrame(outfit_products)
            
            # Cache the data
            if use_cache and not df.empty:
                self.data_loader.cache_data(df, cache_key)
            
            logger.info(f"Successfully loaded outfit products ({len(df)} records)")
            return df
            
        except Exception as e:
            logger.error(f"Error loading outfit products: {str(e)}")
            return pd.DataFrame()
    
    def load_color_suggestions(self, use_cache: bool = True) -> pd.DataFrame:
        """
        Load color suggestions data with validation and caching.
        
        Args:
            use_cache: Whether to use cached data if available
            
        Returns:
            pd.DataFrame: Color suggestions data
        """
        cache_key = "color_suggestions"
        
        # Try to load from cache first
        if use_cache:
            cached_data = self.data_loader.load_from_cache(cache_key)
            if cached_data is not None:
                logger.info("Loaded color suggestions from cache")
                return cached_data
        
        # Load from files
        try:
            df = self.data_loader.load_csv_with_fallback(
                primary_path="processed_data/color_suggestions.csv",
                fallback_paths=["color_suggestions.csv"],
                required_columns=["skin_tone"],
                default_df=pd.DataFrame(columns=["skin_tone", "suitable_colors"])
            )
            
            # Cache the data
            if use_cache and not df.empty:
                self.data_loader.cache_data(df, cache_key)
            
            logger.info(f"Successfully loaded color suggestions ({len(df)} records)")
            return df
            
        except Exception as e:
            logger.error(f"Error loading color suggestions: {str(e)}")
            return pd.DataFrame()
    
    def load_seasonal_palettes_json(self, use_cache: bool = True) -> Dict[str, Any]:
        """
        Load seasonal palettes JSON data with validation and caching.
        
        Args:
            use_cache: Whether to use cached data if available
            
        Returns:
            Dict[str, Any]: Seasonal palettes data
        """
        cache_key = "seasonal_palettes_json"
        
        # Try to load from cache first
        if use_cache:
            cached_data = self.data_loader.load_from_cache(cache_key)
            if cached_data is not None:
                logger.info("Loaded seasonal palettes from cache")
                return cached_data
        
        # Load from files
        try:
            data = self.data_loader.load_json_with_fallback(
                primary_path=str(self.data_dir / "seasonal_palettes.json"),
                fallback_paths=[
                    "processed_data/seasonal_palettes.json",
                    "seasonal_palettes.json"
                ],
                default_data={}
            )
            
            # Cache the data
            if use_cache and data:
                self.data_loader.cache_data(data, cache_key)
            
            logger.info(f"Successfully loaded seasonal palettes JSON")
            return data
            
        except Exception as e:
            logger.error(f"Error loading seasonal palettes JSON: {str(e)}")
            return {}
    
    def get_dataset(self, dataset_name: str, use_cache: bool = True) -> pd.DataFrame:
        """
        Get a specific dataset by name with caching.
        
        Args:
            dataset_name: Name of the dataset to load
            use_cache: Whether to use cached data if available
            
        Returns:
            pd.DataFrame: Requested dataset
        """
        # Check if already loaded
        if dataset_name in self._datasets and not use_cache:
            return self._datasets[dataset_name]
        
        # Load based on dataset name
        if dataset_name == "hm_products":
            df = self.load_hm_products(use_cache)
        elif dataset_name == "makeup_products":
            df = self.load_makeup_products(use_cache)
        elif dataset_name == "outfit_products":
            df = self.load_outfit_products(use_cache)
        elif dataset_name == "color_suggestions":
            df = self.load_color_suggestions(use_cache)
        else:
            logger.warning(f"Unknown dataset: {dataset_name}")
            return pd.DataFrame()
        
        # Cache in memory
        self._datasets[dataset_name] = df
        return df
    
    def refresh_cache(self):
        """Refresh all cached data by reloading from source files."""
        logger.info("Refreshing all cached data...")
        
        # Clear memory cache
        self._datasets.clear()
        
        # Reload all datasets without using cache
        datasets = ["hm_products", "makeup_products", "outfit_products", "color_suggestions"]
        for dataset_name in datasets:
            try:
                self.get_dataset(dataset_name, use_cache=False)
                logger.info(f"Refreshed {dataset_name}")
            except Exception as e:
                logger.error(f"Error refreshing {dataset_name}: {str(e)}")
        
        # Reload JSON data
        try:
            self.load_seasonal_palettes_json(use_cache=False)
            logger.info("Refreshed seasonal palettes JSON")
        except Exception as e:
            logger.error(f"Error refreshing seasonal palettes JSON: {str(e)}")
        
        logger.info("Cache refresh completed")
    
    def get_dataset_info(self) -> Dict[str, Any]:
        """
        Get information about all loaded datasets.
        
        Returns:
            Dict[str, Any]: Information about datasets
        """
        info = {}
        datasets = ["hm_products", "makeup_products", "outfit_products", "color_suggestions"]
        
        for dataset_name in datasets:
            try:
                df = self.get_dataset(dataset_name)
                info[dataset_name] = {
                    "rows": len(df),
                    "columns": list(df.columns),
                    "memory_usage": df.memory_usage(deep=True).sum()
                }
            except Exception as e:
                info[dataset_name] = {"error": str(e)}
        
        return info


# Global data service instance
_data_service = None


def get_data_service(data_dir: str = None, cache_dir: str = "cache") -> DataService:
    """
    Get the global data service instance (singleton pattern).
    
    Args:
        data_dir: Directory containing data files
        cache_dir: Directory for caching processed data
        
    Returns:
        DataService: The global data service instance
    """
    global _data_service
    
    if _data_service is None:
        _data_service = DataService(data_dir, cache_dir)
    
    return _data_service
