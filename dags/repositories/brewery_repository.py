"""
Brewery Repository Implementations

Concrete implementations of IBreweryRepository.
"""

from typing import List, Optional, Dict
from domain import Brewery
from domain.exceptions import EntityNotFoundError, DuplicateEntityError
from .base import IBreweryRepository
from utils import get_logger


class InMemoryBreweryRepository(IBreweryRepository):
    """
    In-memory brewery repository for testing.

    Stores breweries in a dictionary for fast access.
    Useful for unit tests and development.

    Example:
        >>> repo = InMemoryBreweryRepository()
        >>>
        >>> # Add brewery
        >>> brewery = Brewery(id="1", name="Test Brewery", ...)
        >>> repo.add(brewery)
        >>>
        >>> # Get brewery
        >>> found = repo.get_by_id("1")
        >>> assert found.id == "1"
        >>>
        >>> # Query
        >>> craft = repo.get_craft()
        >>> active = repo.get_active()
    """

    def __init__(self):
        """Initialize in-memory repository."""
        self._breweries: Dict[str, Brewery] = {}
        self.logger = get_logger(__name__)

    def get_by_id(self, id: str) -> Optional[Brewery]:
        """Get brewery by ID."""
        return self._breweries.get(id)

    def get_all(self) -> List[Brewery]:
        """Get all breweries."""
        return list(self._breweries.values())

    def add(self, entity: Brewery) -> None:
        """
        Add brewery to repository.

        Raises:
            DuplicateEntityError: If brewery with same ID exists
        """
        if entity.id in self._breweries:
            raise DuplicateEntityError(
                f"Brewery with id '{entity.id}' already exists",
                details={"id": entity.id, "name": entity.name},
            )

        self._breweries[entity.id] = entity
        self.logger.debug(f"Added brewery: {entity.id}")

    def add_many(self, entities: List[Brewery]) -> None:
        """Add multiple breweries."""
        for entity in entities:
            # Check for duplicates first
            if entity.id in self._breweries:
                self.logger.warning(f"Skipping duplicate brewery: {entity.id}")
                continue
            self._breweries[entity.id] = entity

        self.logger.info(f"Added {len(entities)} breweries")

    def update(self, entity: Brewery) -> None:
        """
        Update existing brewery.

        Raises:
            EntityNotFoundError: If brewery doesn't exist
        """
        if entity.id not in self._breweries:
            raise EntityNotFoundError(
                f"Brewery with id '{entity.id}' not found", details={"id": entity.id}
            )

        self._breweries[entity.id] = entity
        self.logger.debug(f"Updated brewery: {entity.id}")

    def remove(self, entity: Brewery) -> None:
        """
        Remove brewery from repository.

        Raises:
            EntityNotFoundError: If brewery doesn't exist
        """
        if entity.id not in self._breweries:
            raise EntityNotFoundError(
                f"Brewery with id '{entity.id}' not found", details={"id": entity.id}
            )

        del self._breweries[entity.id]
        self.logger.debug(f"Removed brewery: {entity.id}")

    def count(self) -> int:
        """Count total breweries."""
        return len(self._breweries)

    def exists(self, id: str) -> bool:
        """Check if brewery exists."""
        return id in self._breweries

    def get_by_name(self, name: str) -> Optional[Brewery]:
        """Get brewery by name (case-insensitive)."""
        for brewery in self._breweries.values():
            if brewery.name.lower() == name.lower():
                return brewery
        return None

    def get_by_type(self, brewery_type: str) -> List[Brewery]:
        """Get breweries by type."""
        return [
            brewery
            for brewery in self._breweries.values()
            if str(brewery.brewery_type).lower() == brewery_type.lower()
        ]

    def get_by_city(self, city: str) -> List[Brewery]:
        """Get breweries by city."""
        return [
            brewery
            for brewery in self._breweries.values()
            if brewery.location
            and brewery.location.address.city.lower() == city.lower()
        ]

    def get_by_state(self, state: str) -> List[Brewery]:
        """Get breweries by state."""
        return [
            brewery
            for brewery in self._breweries.values()
            if brewery.location
            and brewery.location.address.state.lower() == state.lower()
        ]

    def get_active(self) -> List[Brewery]:
        """Get all active breweries."""
        return [brewery for brewery in self._breweries.values() if brewery.is_active()]

    def get_craft(self) -> List[Brewery]:
        """Get all craft breweries."""
        return [brewery for brewery in self._breweries.values() if brewery.is_craft()]

    def search(self, query: str) -> List[Brewery]:
        """Search breweries by name or location."""
        query_lower = query.lower()
        results = []

        for brewery in self._breweries.values():
            # Search in name
            if query_lower in brewery.name.lower():
                results.append(brewery)
                continue

            # Search in location
            if brewery.location:
                address = brewery.location.address
                if (
                    query_lower in address.city.lower()
                    or query_lower in address.state.lower()
                ):
                    results.append(brewery)

        return results

    def clear(self) -> None:
        """Clear all breweries (useful for testing)."""
        self._breweries.clear()
        self.logger.debug("Cleared all breweries")


class SQLBreweryRepository(IBreweryRepository):
    """
    SQL database brewery repository.

    Implements repository pattern for SQL database access.
    Uses provided loader for actual persistence.

    Example:
        >>> from services import AzureSQLLoader
        >>> loader = AzureSQLLoader(config)
        >>> repo = SQLBreweryRepository(loader)
        >>>
        >>> # Add brewery
        >>> brewery = Brewery(...)
        >>> repo.add(brewery)
        >>>
        >>> # Query (fetches from database)
        >>> all_breweries = repo.get_all()
    """

    def __init__(self, loader):
        """
        Initialize SQL repository.

        Args:
            loader: Data loader for database access (IDataLoader)
        """
        self.loader = loader
        self.logger = get_logger(__name__)
        self._cache: Dict[str, Brewery] = {}
        self._dirty: set = set()  # Track unsaved changes

    def get_by_id(self, id: str) -> Optional[Brewery]:
        """
        Get brewery by ID.

        Checks cache first, then database.
        """
        # Check cache
        if id in self._cache:
            return self._cache[id]

        # Query database
        # Note: This is a simplified implementation
        # Real implementation would use SQL queries
        all_breweries = self.get_all()
        for brewery in all_breweries:
            if brewery.id == id:
                self._cache[id] = brewery
                return brewery

        return None

    def get_all(self) -> List[Brewery]:
        """
        Get all breweries from database.

        Note: This loads all data into memory.
        For large datasets, implement pagination.
        """
        try:
            # Extract data from database
            # This assumes loader can read data (might need separate reader)
            from domain import Brewery

            # For now, return cached breweries
            # Real implementation would query database
            self.logger.warning(
                "get_all() using cache only. "
                "Full database query not yet implemented."
            )
            return list(self._cache.values())

        except Exception as e:
            self.logger.error(f"Error fetching breweries: {e}")
            return []

    def add(self, entity: Brewery) -> None:
        """
        Add brewery to repository.

        Marks as dirty for later persistence.
        """
        if self.exists(entity.id):
            raise DuplicateEntityError(
                f"Brewery with id '{entity.id}' already exists",
                details={"id": entity.id},
            )

        self._cache[entity.id] = entity
        self._dirty.add(entity.id)
        self.logger.debug(f"Added brewery to cache: {entity.id}")

    def add_many(self, entities: List[Brewery]) -> None:
        """Add multiple breweries."""
        for entity in entities:
            if not self.exists(entity.id):
                self._cache[entity.id] = entity
                self._dirty.add(entity.id)

        self.logger.info(f"Added {len(entities)} breweries to cache")

    def update(self, entity: Brewery) -> None:
        """Update existing brewery."""
        if not self.exists(entity.id):
            raise EntityNotFoundError(
                f"Brewery with id '{entity.id}' not found", details={"id": entity.id}
            )

        self._cache[entity.id] = entity
        self._dirty.add(entity.id)
        self.logger.debug(f"Updated brewery in cache: {entity.id}")

    def remove(self, entity: Brewery) -> None:
        """Remove brewery."""
        if not self.exists(entity.id):
            raise EntityNotFoundError(
                f"Brewery with id '{entity.id}' not found", details={"id": entity.id}
            )

        del self._cache[entity.id]
        self._dirty.discard(entity.id)
        self.logger.debug(f"Removed brewery from cache: {entity.id}")

    def count(self) -> int:
        """Count total breweries (from cache)."""
        return len(self._cache)

    def exists(self, id: str) -> bool:
        """Check if brewery exists (in cache)."""
        return id in self._cache

    def save(self) -> int:
        """
        Persist all changes to database.

        Returns:
            Number of records saved
        """
        if not self._dirty:
            self.logger.info("No changes to save")
            return 0

        # Get dirty breweries
        breweries_to_save = [self._cache[id] for id in self._dirty if id in self._cache]

        if not breweries_to_save:
            return 0

        # Convert to dicts for loader
        data = [brewery.to_dict() for brewery in breweries_to_save]

        # Ensure table exists
        self.loader.create_table_if_not_exists()

        # Load data
        loaded_count = self.loader.load(data)

        # Clear dirty flag
        self._dirty.clear()

        self.logger.info(f"Saved {loaded_count} breweries to database")
        return loaded_count

    # Brewery-specific queries

    def get_by_name(self, name: str) -> Optional[Brewery]:
        """Get brewery by name."""
        for brewery in self._cache.values():
            if brewery.name.lower() == name.lower():
                return brewery
        return None

    def get_by_type(self, brewery_type: str) -> List[Brewery]:
        """Get breweries by type."""
        return [
            brewery
            for brewery in self._cache.values()
            if str(brewery.brewery_type).lower() == brewery_type.lower()
        ]

    def get_by_city(self, city: str) -> List[Brewery]:
        """Get breweries by city."""
        return [
            brewery
            for brewery in self._cache.values()
            if brewery.location
            and brewery.location.address.city.lower() == city.lower()
        ]

    def get_by_state(self, state: str) -> List[Brewery]:
        """Get breweries by state."""
        return [
            brewery
            for brewery in self._cache.values()
            if brewery.location
            and brewery.location.address.state.lower() == state.lower()
        ]

    def get_active(self) -> List[Brewery]:
        """Get all active breweries."""
        return [brewery for brewery in self._cache.values() if brewery.is_active()]

    def get_craft(self) -> List[Brewery]:
        """Get all craft breweries."""
        return [brewery for brewery in self._cache.values() if brewery.is_craft()]

    def search(self, query: str) -> List[Brewery]:
        """Search breweries."""
        query_lower = query.lower()
        results = []

        for brewery in self._cache.values():
            if query_lower in brewery.name.lower():
                results.append(brewery)
                continue

            if brewery.location:
                address = brewery.location.address
                if (
                    query_lower in address.city.lower()
                    or query_lower in address.state.lower()
                ):
                    results.append(brewery)

        return results
