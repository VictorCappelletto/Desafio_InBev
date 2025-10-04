"""
ETL Factory

Factory class for creating ETL components.

Design Patterns Applied:
- Factory Pattern: Centralizes object creation logic
- Dependency Injection: Injects configurations into services
- Abstract Factory: Returns interfaces, not concrete types

SOLID Principles:
- Single Responsibility: Only creates objects, doesn't use them
- Open/Closed: Easy to add new factories without modifying existing ones
- Dependency Inversion: Depends on interfaces (IDataExtractor, etc.)

Benefits:
- Centralized object creation
- Easy to swap implementations
- Configuration management in one place
- Testable (can create mocks easily)
"""

from typing import Tuple, Optional

# Import from config package (not config.settings directly)
from config import (
    AzureSQLConfig,
    DatabricksConfig,
    AzureDataFactoryConfig,
    APIConfig,
)

# Services
from services.brewery_api_extractor import BreweryAPIExtractor
from services.azure_sql_loader import AzureSQLLoader
from services.brewery_transformer import BreweryTransformer

# Interfaces
from interfaces.data_extractor import IDataExtractor
from interfaces.data_loader import IDataLoader
from interfaces.data_transformer import IDataTransformer


class ETLFactory:
    """
    Factory for creating ETL components.
    
    This class demonstrates:
    - Factory Pattern: Centralizes object creation
    - Dependency Injection: Injects configurations into services
    - Single Responsibility: Only creates objects
    - Open/Closed: Easy to add new factories without changing existing code
    """
    
    @staticmethod
    def create_brewery_extractor(config: Optional[APIConfig] = None) -> IDataExtractor:
        """
        Create brewery API extractor with dependency injection.
        
        Factory method that creates a BreweryAPIExtractor instance with
        proper configuration injection.
        
        Args:
            config: API configuration. If None, creates default config
                   from environment variables.
            
        Returns:
            IDataExtractor: Configured BreweryAPIExtractor instance
            
        Example:
            >>> factory = ETLFactory()
            >>> extractor = factory.create_brewery_extractor()
            >>> data = extractor.extract()
        """
        if config is None:
            config = APIConfig()
        
        return BreweryAPIExtractor(config)
    
    @staticmethod
    def create_azure_sql_loader(
        config: Optional[AzureSQLConfig] = None,
        table_name: str = "Breweries"
    ) -> IDataLoader:
        """
        Create Azure SQL loader with dependency injection.
        
        Factory method that creates an AzureSQLLoader instance with
        proper configuration and table name.
        
        Args:
            config: Azure SQL configuration. If None, creates default config
                   from environment variables.
            table_name: Target table name for loading data.
            
        Returns:
            IDataLoader: Configured AzureSQLLoader instance
            
        Example:
            >>> loader = ETLFactory.create_azure_sql_loader(table_name="MyTable")
            >>> loader.load(data)
        """
        if config is None:
            config = AzureSQLConfig()
        
        return AzureSQLLoader(config, table_name=table_name)
    
    @staticmethod
    def create_brewery_transformer() -> IDataTransformer:
        """
        Create brewery data transformer.
        
        Factory method that creates a BreweryTransformer instance.
        Transformers typically don't need configuration.
        
        Returns:
            IDataTransformer: BreweryTransformer instance
            
        Example:
            >>> transformer = ETLFactory.create_brewery_transformer()
            >>> clean_data = transformer.transform(raw_data)
        """
        return BreweryTransformer()
    
    @staticmethod
    def create_etl_pipeline(
        api_config: Optional[APIConfig] = None,
        sql_config: Optional[AzureSQLConfig] = None,
        table_name: str = "Breweries"
    ) -> Tuple[IDataExtractor, IDataTransformer, IDataLoader]:
        """
        Create complete ETL pipeline with all components.
        
        Convenience method that creates all three ETL components at once
        with proper configuration injection.
        
        Args:
            api_config: API configuration for extractor (optional)
            sql_config: SQL configuration for loader (optional)
            table_name: Target table name for loader
        
        Returns:
            Tuple[IDataExtractor, IDataTransformer, IDataLoader]:
                Complete ETL pipeline components (extractor, transformer, loader)
                
        Example:
            >>> extractor, transformer, loader = ETLFactory.create_etl_pipeline()
            >>> 
            >>> # Use in DAG
            >>> raw_data = extractor.extract()
            >>> clean_data = transformer.transform(raw_data)
            >>> loader.load(clean_data)
        """
        extractor = ETLFactory.create_brewery_extractor(api_config)
        transformer = ETLFactory.create_brewery_transformer()
        loader = ETLFactory.create_azure_sql_loader(sql_config, table_name)
        
        return extractor, transformer, loader

