"""
Integration Tests - Domain Layer

Tests domain entities, value objects, and business logic.
"""

import pytest
from datetime import datetime

from domain import (
    Brewery,
    BreweryAggregate,
    BreweryType,
    Coordinates,
    Address,
    Location,
    Contact,
)
from domain.exceptions import (
    InvalidCoordinatesError,
    InvalidBreweryNameError,
    InvalidBreweryTypeError,
)
from domain.validators import BreweryValidator, LocationValidator


class TestValueObjects:
    """Test immutable value objects."""

    def test_coordinates_valid(self):
        """Test creating valid coordinates."""
        coords = Coordinates(latitude=37.7749, longitude=-122.4194)

        assert coords.latitude == 37.7749
        assert coords.longitude == -122.4194

    def test_coordinates_invalid_latitude(self):
        """Test coordinates with invalid latitude."""
        with pytest.raises(InvalidCoordinatesError):
            Coordinates(latitude=100.0, longitude=-122.4194)

        with pytest.raises(InvalidCoordinatesError):
            Coordinates(latitude=-100.0, longitude=-122.4194)

    def test_coordinates_invalid_longitude(self):
        """Test coordinates with invalid longitude."""
        with pytest.raises(InvalidCoordinatesError):
            Coordinates(latitude=37.7749, longitude=200.0)

        with pytest.raises(InvalidCoordinatesError):
            Coordinates(latitude=37.7749, longitude=-200.0)

    def test_coordinates_immutable(self):
        """Test coordinates are immutable."""
        coords = Coordinates(latitude=37.7749, longitude=-122.4194)

        with pytest.raises(Exception):  # FrozenInstanceError
            coords.latitude = 50.0

    def test_address_valid(self):
        """Test creating valid address."""
        address = Address(
            street="123 Main St",
            city="San Francisco",
            state="California",
            postal_code="94102",
        )

        assert address.city == "San Francisco"
        assert address.state == "California"

    def test_address_immutable(self):
        """Test address is immutable."""
        address = Address(city="San Francisco", state="California")

        with pytest.raises(Exception):  # FrozenInstanceError
            address.city = "Los Angeles"

    def test_location_with_full_data(self):
        """Test location with coordinates and address."""
        coords = Coordinates(37.7749, -122.4194)
        address = Address(
            street="123 Main St",
            city="San Francisco",
            state="California",
            postal_code="94102",
        )
        location = Location(coordinates=coords, address=address)

        assert location.coordinates is not None
        assert location.address is not None
        assert location.coordinates.latitude == 37.7749

    def test_contact_with_valid_data(self):
        """Test contact value object."""
        contact = Contact(
            phone="555-1234",
            website_url="https://brewery.com",
            email="info@brewery.com",
        )

        assert contact.phone == "555-1234"
        assert contact.website_url == "https://brewery.com"

    def test_brewery_type_enum(self):
        """Test BreweryType enum."""
        assert BreweryType.MICRO.value == "micro"
        assert BreweryType.NANO.value == "nano"
        assert BreweryType.REGIONAL.value == "regional"

        # Test from string
        micro_type = BreweryType("micro")
        assert micro_type == BreweryType.MICRO


class TestBreweryEntity:
    """Test Brewery entity."""

    def test_brewery_creation_minimal(self):
        """Test creating brewery with minimal data."""
        brewery = Brewery(
            id="test-1", name="Test Brewery", brewery_type=BreweryType.MICRO
        )

        assert brewery.id == "test-1"
        assert brewery.name == "Test Brewery"
        assert brewery.brewery_type == BreweryType.MICRO

    def test_brewery_creation_full(self):
        """Test creating brewery with full data."""
        coords = Coordinates(37.7749, -122.4194)
        address = Address(
            street="123 Main St",
            city="San Francisco",
            state="California",
            postal_code="94102",
        )
        location = Location(coordinates=coords, address=address)
        contact = Contact(phone="555-1234", website_url="https://test.com")

        brewery = Brewery(
            id="test-full",
            name="Full Brewery",
            brewery_type=BreweryType.MICRO,
            location=location,
            contact=contact,
        )

        assert brewery.location is not None
        assert brewery.contact is not None
        assert brewery.location.coordinates.latitude == 37.7749

    def test_brewery_from_dict_valid(self):
        """Test factory method from_dict with valid data."""
        data = {
            "id": "dict-test",
            "name": "Dict Brewery",
            "brewery_type": "micro",
            "latitude": "37.7749",
            "longitude": "-122.4194",
            "street": "123 Main St",
            "city": "San Francisco",
            "state": "California",
            "postal_code": "94102",
            "phone": "555-1234",
            "website_url": "https://test.com",
        }

        brewery = Brewery.from_dict(data)

        assert brewery.id == "dict-test"
        assert brewery.name == "Dict Brewery"
        assert brewery.brewery_type == BreweryType.MICRO
        assert brewery.location is not None
        assert brewery.location.coordinates.latitude == 37.7749

    def test_brewery_from_dict_minimal(self):
        """Test from_dict with minimal data."""
        data = {
            "id": "minimal",
            "name": "Minimal Brewery",
            "brewery_type": "micro",
        }

        brewery = Brewery.from_dict(data)

        assert brewery.id == "minimal"
        assert brewery.name == "Minimal Brewery"
        assert brewery.location is None
        assert brewery.contact is None

    def test_brewery_invalid_name(self):
        """Test brewery with invalid name."""
        with pytest.raises(InvalidBreweryNameError):
            Brewery(id="test", name="", brewery_type=BreweryType.MICRO)

    def test_brewery_invalid_type(self):
        """Test brewery with invalid type."""
        with pytest.raises(InvalidBreweryTypeError):
            Brewery(id="test", name="Test", brewery_type="invalid_type")


class TestBreweryAggregate:
    """Test Brewery aggregate root."""

    @pytest.fixture
    def sample_brewery(self):
        """Sample brewery with full data."""
        coords = Coordinates(37.7749, -122.4194)
        address = Address(
            street="123 Main St",
            city="San Francisco",
            state="California",
            postal_code="94102",
        )
        location = Location(coordinates=coords, address=address)
        contact = Contact(phone="555-1234", website_url="https://test.com")

        return Brewery(
            id="aggregate-test",
            name="Aggregate Brewery",
            brewery_type=BreweryType.MICRO,
            location=location,
            contact=contact,
        )

    def test_aggregate_creation(self, sample_brewery):
        """Test creating brewery aggregate."""
        aggregate = BreweryAggregate(sample_brewery)

        assert aggregate.brewery.id == "aggregate-test"
        assert aggregate.brewery.name == "Aggregate Brewery"

    def test_aggregate_calculate_quality_score_high(self, sample_brewery):
        """Test quality score calculation for complete data."""
        aggregate = BreweryAggregate(sample_brewery)
        score = aggregate.calculate_quality_score()

        # Full data should have high score
        assert score > 0.8
        assert score <= 1.0

    def test_aggregate_calculate_quality_score_low(self):
        """Test quality score for minimal data."""
        minimal_brewery = Brewery(
            id="minimal", name="Minimal", brewery_type=BreweryType.MICRO
        )

        aggregate = BreweryAggregate(minimal_brewery)
        score = aggregate.calculate_quality_score()

        # Minimal data should have lower score
        assert score >= 0.5  # Base score
        assert score < 0.8

    def test_aggregate_from_dict(self):
        """Test creating aggregate from dictionary."""
        data = {
            "id": "agg-dict",
            "name": "Dict Aggregate",
            "brewery_type": "micro",
        }

        aggregate = BreweryAggregate.from_dict(data)

        assert aggregate.brewery.id == "agg-dict"
        assert aggregate.brewery.name == "Dict Aggregate"

    def test_aggregate_quality_factors(self):
        """Test individual quality factors."""
        # Test with varying levels of completeness
        test_cases = [
            (
                {"id": "1", "name": "Min", "brewery_type": "micro"},
                0.5,  # Base score only
            ),
            (
                {
                    "id": "2",
                    "name": "With Location",
                    "brewery_type": "micro",
                    "city": "SF",
                    "state": "CA",
                },
                0.7,  # Base + location
            ),
        ]

        for data, min_expected_score in test_cases:
            aggregate = BreweryAggregate.from_dict(data)
            score = aggregate.calculate_quality_score()
            assert score >= min_expected_score


class TestValidators:
    """Test domain validators."""

    def test_brewery_validator_valid_name(self):
        """Test name validation with valid name."""
        # Should not raise
        BreweryValidator.validate_name("Valid Brewery Name")

    def test_brewery_validator_invalid_name(self):
        """Test name validation with invalid names."""
        with pytest.raises(InvalidBreweryNameError):
            BreweryValidator.validate_name("")

        with pytest.raises(InvalidBreweryNameError):
            BreweryValidator.validate_name("  ")

        with pytest.raises(InvalidBreweryNameError):
            BreweryValidator.validate_name("X")  # Too short

    def test_brewery_validator_valid_type(self):
        """Test type validation with valid types."""
        valid_types = ["micro", "nano", "regional", "brewpub", "large"]

        for brewery_type in valid_types:
            # Should not raise
            BreweryValidator.validate_type(brewery_type)

    def test_brewery_validator_invalid_type(self):
        """Test type validation with invalid type."""
        with pytest.raises(InvalidBreweryTypeError):
            BreweryValidator.validate_type("invalid_type")

    def test_location_validator_valid_coordinates(self):
        """Test coordinate validation with valid values."""
        # Should not raise
        LocationValidator.validate_coordinates(37.7749, -122.4194)
        LocationValidator.validate_coordinates(0.0, 0.0)
        LocationValidator.validate_coordinates(90.0, 180.0)
        LocationValidator.validate_coordinates(-90.0, -180.0)

    def test_location_validator_invalid_coordinates(self):
        """Test coordinate validation with invalid values."""
        with pytest.raises(InvalidCoordinatesError):
            LocationValidator.validate_coordinates(100.0, -122.4194)

        with pytest.raises(InvalidCoordinatesError):
            LocationValidator.validate_coordinates(37.7749, 200.0)
