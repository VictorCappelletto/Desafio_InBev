"""
Base Repository Interfaces

Abstract interfaces for all repositories.
Concrete implementations must implement these interfaces.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Generic, TypeVar
from domain import Brewery


# Generic type for entities
T = TypeVar('T')


class IRepository(ABC, Generic[T]):
    """
    Base repository interface.
    
    Provides collection-like interface for domain entities.
    All repositories should implement this interface.
    
    Type Parameters:
        T: Type of entity (e.g., Brewery)
    
    Example:
        class UserRepository(IRepository[User]):
            def get_by_id(self, id: str) -> Optional[User]:
                # Implementation
                pass
    """
    
    @abstractmethod
    def get_by_id(self, id: str) -> Optional[T]:
        """
        Get entity by ID.
        
        Args:
            id: Entity identifier
        
        Returns:
            Entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    def get_all(self) -> List[T]:
        """
        Get all entities.
        
        Returns:
            List of all entities
        """
        pass
    
    @abstractmethod
    def add(self, entity: T) -> None:
        """
        Add entity to repository.
        
        Args:
            entity: Entity to add
        """
        pass
    
    @abstractmethod
    def add_many(self, entities: List[T]) -> None:
        """
        Add multiple entities.
        
        Args:
            entities: List of entities to add
        """
        pass
    
    @abstractmethod
    def update(self, entity: T) -> None:
        """
        Update existing entity.
        
        Args:
            entity: Entity with updated data
        """
        pass
    
    @abstractmethod
    def remove(self, entity: T) -> None:
        """
        Remove entity from repository.
        
        Args:
            entity: Entity to remove
        """
        pass
    
    @abstractmethod
    def count(self) -> int:
        """
        Count total entities.
        
        Returns:
            Total number of entities
        """
        pass
    
    @abstractmethod
    def exists(self, id: str) -> bool:
        """
        Check if entity exists.
        
        Args:
            id: Entity identifier
        
        Returns:
            True if exists, False otherwise
        """
        pass


class IBreweryRepository(IRepository[Brewery]):
    """
    Brewery-specific repository interface.
    
    Extends base repository with brewery-specific queries.
    
    Example:
        >>> repo = BreweryRepository()
        >>> 
        >>> # Base operations
        >>> brewery = repo.get_by_id("abc-123")
        >>> all_breweries = repo.get_all()
        >>> 
        >>> # Brewery-specific
        >>> craft_breweries = repo.get_by_type("micro")
        >>> portland_breweries = repo.get_by_city("Portland")
        >>> active_breweries = repo.get_active()
    """
    
    @abstractmethod
    def get_by_name(self, name: str) -> Optional[Brewery]:
        """
        Get brewery by name.
        
        Args:
            name: Brewery name
        
        Returns:
            Brewery if found, None otherwise
        """
        pass
    
    @abstractmethod
    def get_by_type(self, brewery_type: str) -> List[Brewery]:
        """
        Get breweries by type.
        
        Args:
            brewery_type: Type of brewery (micro, nano, etc.)
        
        Returns:
            List of breweries matching type
        """
        pass
    
    @abstractmethod
    def get_by_city(self, city: str) -> List[Brewery]:
        """
        Get breweries by city.
        
        Args:
            city: City name
        
        Returns:
            List of breweries in city
        """
        pass
    
    @abstractmethod
    def get_by_state(self, state: str) -> List[Brewery]:
        """
        Get breweries by state.
        
        Args:
            state: State name
        
        Returns:
            List of breweries in state
        """
        pass
    
    @abstractmethod
    def get_active(self) -> List[Brewery]:
        """
        Get all active breweries.
        
        Returns:
            List of active breweries
        """
        pass
    
    @abstractmethod
    def get_craft(self) -> List[Brewery]:
        """
        Get all craft breweries.
        
        Returns:
            List of craft breweries
        """
        pass
    
    @abstractmethod
    def search(self, query: str) -> List[Brewery]:
        """
        Search breweries by name or location.
        
        Args:
            query: Search query
        
        Returns:
            List of matching breweries
        """
        pass

