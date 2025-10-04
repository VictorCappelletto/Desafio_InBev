"""
Integration Tests - Repository Pattern

Tests repository implementations and Unit of Work pattern.
"""

from typing import List

import pytest
from domain import Address, Brewery, BreweryType, Coordinates, Location
from domain.exceptions import DuplicateBreweryError, EntityNotFoundError
from repositories import InMemoryBreweryRepository, UnitOfWork


class TestInMemoryBreweryRepository:
    """Test InMemoryBreweryRepository implementation."""

    @pytest.fixture
    def repository(self):
        """Fresh repository for each test."""
        return InMemoryBreweryRepository()

    @pytest.fixture
    def sample_brewery(self):
        """Sample brewery entity."""
        return Brewery(
            id="test-1",
            name="Test Brewery",
            brewery_type=BreweryType.MICRO,
            location=Location(
                coordinates=Coordinates(37.7749, -122.4194),
                address=Address(
                    street="123 Main St",
                    city="San Francisco",
                    state="California",
                    postal_code="94102",
                ),
            ),
        )

    def test_add_and_get_by_id(self, repository, sample_brewery):
        """Test adding and retrieving brewery."""
        repository.add(sample_brewery)

        retrieved = repository.get_by_id("test-1")
        assert retrieved is not None
        assert retrieved.id == "test-1"
        assert retrieved.name == "Test Brewery"

    def test_add_duplicate_raises_error(self, repository, sample_brewery):
        """Test adding duplicate brewery raises error."""
        repository.add(sample_brewery)

        with pytest.raises(DuplicateBreweryError):
            repository.add(sample_brewery)

    def test_get_all(self, repository):
        """Test getting all breweries."""
        brewery1 = Brewery(id="1", name="Brewery 1", brewery_type=BreweryType.MICRO)
        brewery2 = Brewery(id="2", name="Brewery 2", brewery_type=BreweryType.NANO)

        repository.add(brewery1)
        repository.add(brewery2)

        all_breweries = repository.get_all()
        assert len(all_breweries) == 2
        assert {b.id for b in all_breweries} == {"1", "2"}

    def test_add_many(self, repository):
        """Test batch add operation."""
        breweries = [
            Brewery(id=f"{i}", name=f"Brewery {i}", brewery_type=BreweryType.MICRO)
            for i in range(5)
        ]

        count = repository.add_many(breweries)
        assert count == 5
        assert repository.count() == 5

    def test_update(self, repository, sample_brewery):
        """Test updating brewery."""
        repository.add(sample_brewery)

        # Update name
        sample_brewery.name = "Updated Brewery"
        repository.update(sample_brewery)

        retrieved = repository.get_by_id("test-1")
        assert retrieved.name == "Updated Brewery"

    def test_remove(self, repository, sample_brewery):
        """Test removing brewery."""
        repository.add(sample_brewery)
        assert repository.count() == 1

        removed = repository.remove("test-1")
        assert removed is True
        assert repository.count() == 0
        assert repository.get_by_id("test-1") is None

    def test_exists(self, repository, sample_brewery):
        """Test checking brewery existence."""
        assert repository.exists("test-1") is False

        repository.add(sample_brewery)
        assert repository.exists("test-1") is True

    def test_find_by_type(self, repository):
        """Test finding breweries by type."""
        micro1 = Brewery(id="1", name="Micro 1", brewery_type=BreweryType.MICRO)
        micro2 = Brewery(id="2", name="Micro 2", brewery_type=BreweryType.MICRO)
        nano = Brewery(id="3", name="Nano 1", brewery_type=BreweryType.NANO)

        repository.add_many([micro1, micro2, nano])

        micros = repository.find_by_type("micro")
        assert len(micros) == 2
        assert all(b.brewery_type == BreweryType.MICRO for b in micros)

    def test_find_by_location(self, repository):
        """Test finding breweries by location."""
        sf_brewery = Brewery(
            id="1",
            name="SF Brewery",
            brewery_type=BreweryType.MICRO,
            location=Location(
                address=Address(city="San Francisco", state="California")
            ),
        )
        la_brewery = Brewery(
            id="2",
            name="LA Brewery",
            brewery_type=BreweryType.MICRO,
            location=Location(address=Address(city="Los Angeles", state="California")),
        )

        repository.add_many([sf_brewery, la_brewery])

        sf_results = repository.find_by_location("San Francisco", "California")
        assert len(sf_results) == 1
        assert sf_results[0].id == "1"

    def test_find_by_flexible_criteria(self, repository):
        """Test flexible find_by with multiple criteria."""
        brewery1 = Brewery(
            id="1",
            name="Test Micro",
            brewery_type=BreweryType.MICRO,
            location=Location(
                address=Address(city="San Francisco", state="California")
            ),
        )
        brewery2 = Brewery(
            id="2",
            name="Test Nano",
            brewery_type=BreweryType.NANO,
            location=Location(
                address=Address(city="San Francisco", state="California")
            ),
        )

        repository.add_many([brewery1, brewery2])

        # Find by type
        results = repository.find_by(brewery_type="micro")
        assert len(results) == 1
        assert results[0].id == "1"


class TestUnitOfWork:
    """Test Unit of Work pattern."""

    def test_unit_of_work_commit(self):
        """Test successful transaction commit."""
        with UnitOfWork() as uow:
            brewery = Brewery(
                id="test-uow", name="UoW Test", brewery_type=BreweryType.MICRO
            )
            uow.breweries.add(brewery)
            uow.commit()

        # Verify data persisted (using new UoW)
        with UnitOfWork() as uow:
            retrieved = uow.breweries.get_by_id("test-uow")
            assert retrieved is not None
            assert retrieved.name == "UoW Test"

    def test_unit_of_work_rollback_on_error(self):
        """Test automatic rollback on exception."""
        try:
            with UnitOfWork() as uow:
                brewery = Brewery(
                    id="rollback-test",
                    name="Rollback Test",
                    brewery_type=BreweryType.MICRO,
                )
                uow.breweries.add(brewery)
                # Simulate error before commit
                raise Exception("Simulated error")
        except Exception:
            pass  # Expected

        # Verify data NOT persisted
        with UnitOfWork() as uow:
            retrieved = uow.breweries.get_by_id("rollback-test")
            assert retrieved is None

    def test_unit_of_work_multiple_operations(self):
        """Test multiple operations in single transaction."""
        with UnitOfWork() as uow:
            # Add multiple breweries
            breweries = [
                Brewery(
                    id=f"uow-{i}", name=f"Brewery {i}", brewery_type=BreweryType.MICRO
                )
                for i in range(3)
            ]
            uow.breweries.add_many(breweries)

            # Update one
            brewery = uow.breweries.get_by_id("uow-0")
            brewery.name = "Updated Name"
            uow.breweries.update(brewery)

            # Remove one
            uow.breweries.remove("uow-2")

            uow.commit()

        # Verify results
        with UnitOfWork() as uow:
            assert uow.breweries.count() == 2

            updated = uow.breweries.get_by_id("uow-0")
            assert updated.name == "Updated Name"

            removed = uow.breweries.get_by_id("uow-2")
            assert removed is None

    def test_unit_of_work_context_manager(self):
        """Test UoW works correctly as context manager."""
        uow = UnitOfWork()

        with uow:
            assert uow.breweries is not None
            brewery = Brewery(
                id="ctx-test", name="Context Test", brewery_type=BreweryType.MICRO
            )
            uow.breweries.add(brewery)
            uow.commit()

        # UoW should still be usable in new context
        with UnitOfWork() as new_uow:
            retrieved = new_uow.breweries.get_by_id("ctx-test")
            assert retrieved is not None
