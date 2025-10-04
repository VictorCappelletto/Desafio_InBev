"""
Unit of Work Pattern - Transaction Management

Maintains a list of objects affected by a business transaction
and coordinates the writing of changes.
"""

from abc import ABC, abstractmethod
from typing import Optional
from .base import IBreweryRepository
from .brewery_repository import InMemoryBreweryRepository, SQLBreweryRepository
from utils import get_logger


class IUnitOfWork(ABC):
    """
    Unit of Work interface.
    
    Manages transactions across multiple repositories.
    Ensures atomic commits (all or nothing).
    
    Example:
        >>> with UnitOfWork() as uow:
        ...     brewery = Brewery(...)
        ...     uow.breweries.add(brewery)
        ...     uow.commit()  # Saves all changes
    """
    
    breweries: IBreweryRepository
    
    @abstractmethod
    def __enter__(self):
        """Enter context manager."""
        pass
    
    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        pass
    
    @abstractmethod
    def commit(self) -> None:
        """Commit all changes."""
        pass
    
    @abstractmethod
    def rollback(self) -> None:
        """Rollback all changes."""
        pass


class InMemoryUnitOfWork(IUnitOfWork):
    """
    In-memory unit of work for testing.
    
    Uses in-memory repositories and simple transaction management.
    
    Example:
        >>> with InMemoryUnitOfWork() as uow:
        ...     brewery = Brewery(id="1", name="Test", ...)
        ...     uow.breweries.add(brewery)
        ...     uow.commit()
        >>> 
        >>> # Verify
        >>> with InMemoryUnitOfWork() as uow:
        ...     found = uow.breweries.get_by_id("1")
        ...     assert found is not None
    """
    
    def __init__(self):
        """Initialize in-memory unit of work."""
        self.logger = get_logger(__name__)
        self.breweries = InMemoryBreweryRepository()
        self._committed = False
    
    def __enter__(self):
        """Enter context manager."""
        self.logger.debug("Starting in-memory transaction")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        if exc_type is not None:
            self.logger.error(f"Transaction error: {exc_val}")
            self.rollback()
            return False
        
        if not self._committed:
            self.logger.warning("Transaction not committed, rolling back")
            self.rollback()
        
        return True
    
    def commit(self) -> None:
        """Commit all changes."""
        self.logger.info(
            f"Committing transaction: {self.breweries.count()} breweries"
        )
        self._committed = True
    
    def rollback(self) -> None:
        """Rollback all changes."""
        self.logger.info("Rolling back transaction")
        self.breweries.clear()
        self._committed = False


class UnitOfWork(IUnitOfWork):
    """
    Database unit of work.
    
    Manages database transactions across multiple repositories.
    
    Example:
        >>> from services import AzureSQLLoader
        >>> loader = AzureSQLLoader(config)
        >>> 
        >>> with UnitOfWork(loader) as uow:
        ...     # Add breweries
        ...     for brewery in breweries:
        ...         uow.breweries.add(brewery)
        ...     
        ...     # Commit all changes atomically
        ...     uow.commit()
    """
    
    def __init__(self, loader):
        """
        Initialize unit of work.
        
        Args:
            loader: Database loader (IDataLoader)
        """
        self.logger = get_logger(__name__)
        self.loader = loader
        self.breweries: Optional[SQLBreweryRepository] = None
        self._committed = False
    
    def __enter__(self):
        """Enter context manager."""
        self.logger.debug("Starting database transaction")
        self.breweries = SQLBreweryRepository(self.loader)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        if exc_type is not None:
            self.logger.error(f"Transaction error: {exc_val}", exc_info=True)
            self.rollback()
            return False
        
        if not self._committed:
            self.logger.warning("Transaction not committed, rolling back")
            self.rollback()
        
        return True
    
    def commit(self) -> None:
        """
        Commit all changes to database.
        
        Raises:
            Exception: If commit fails
        """
        try:
            if self.breweries is None:
                raise RuntimeError("Unit of work not initialized")
            
            # Save all repositories
            saved_count = self.breweries.save()
            
            self.logger.info(
                f"✅ Transaction committed: {saved_count} records saved"
            )
            self._committed = True
            
        except Exception as e:
            self.logger.error(f"Commit failed: {e}", exc_info=True)
            self.rollback()
            raise
    
    def rollback(self) -> None:
        """Rollback all changes."""
        self.logger.info("Rolling back transaction")
        
        if self.breweries:
            # Clear caches
            self.breweries._cache.clear()
            self.breweries._dirty.clear()
        
        self._committed = False


class UnitOfWorkFactory:
    """
    Factory for creating unit of work instances.
    
    Example:
        >>> factory = UnitOfWorkFactory()
        >>> 
        >>> # Get in-memory for testing
        >>> uow = factory.create_in_memory()
        >>> 
        >>> # Get database for production
        >>> uow = factory.create_database(loader)
    """
    
    @staticmethod
    def create_in_memory() -> InMemoryUnitOfWork:
        """
        Create in-memory unit of work.
        
        Returns:
            InMemoryUnitOfWork instance
        """
        return InMemoryUnitOfWork()
    
    @staticmethod
    def create_database(loader) -> UnitOfWork:
        """
        Create database unit of work.
        
        Args:
            loader: Database loader
        
        Returns:
            UnitOfWork instance
        """
        return UnitOfWork(loader)

