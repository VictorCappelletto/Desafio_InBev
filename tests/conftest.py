"""
Pytest Configuration and Shared Fixtures

This file contains pytest configuration and fixtures that are shared across all tests.
"""

import os
import sys

import pytest

# Add dags directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "dags"))


@pytest.fixture
def sample_brewery_data():
    """
    Fixture providing sample brewery data for testing.

    Returns:
        List of brewery dictionaries
    """
    return [
        {
            "id": "5494",
            "name": "10 Barrel Brewing Co",
            "brewery_type": "micro",
            "address_1": "1501 E St",
            "address_2": None,
            "address_3": None,
            "city": "San Diego",
            "state_province": "California",
            "postal_code": "92101",
            "country": "United States",
            "longitude": -117.129593,
            "latitude": 32.714813,
            "phone": "6195782311",
            "website_url": "http://10barrel.com",
            "state": "California",
            "street": "1501 E St",
        },
        {
            "id": "9094",
            "name": "18th Street Brewery",
            "brewery_type": "micro",
            "address_1": "5417 Oakley Ave",
            "address_2": None,
            "address_3": None,
            "city": "Hammond",
            "state_province": "Indiana",
            "postal_code": "46320",
            "country": "United States",
            "longitude": -87.5,
            "latitude": 41.583,
            "phone": "2193019573",
            "website_url": "http://www.18thstreetbrewery.com",
            "state": "Indiana",
            "street": "5417 Oakley Ave",
        },
    ]


@pytest.fixture
def sample_invalid_brewery_data():
    """
    Fixture providing invalid brewery data for testing validation.

    Returns:
        List of invalid brewery dictionaries
    """
    return [
        {
            "id": "123",
            # Missing 'name' and 'brewery_type'
            "city": "Test City",
        }
    ]


@pytest.fixture
def mock_api_config():
    """
    Fixture providing a mock API configuration.

    Returns:
        APIConfig instance with test values
    """
    from unittest.mock import patch

    from config.settings import APIConfig

    with patch.dict(
        os.environ,
        {
            "BREWERY_API_URL": "http://test-api.com/breweries",
            "API_TIMEOUT": "30",
            "API_RETRY_ATTEMPTS": "3",
        },
    ):
        return APIConfig()


@pytest.fixture
def mock_sql_config():
    """
    Fixture providing a mock SQL configuration.

    Returns:
        AzureSQLConfig instance with test values
    """
    from unittest.mock import patch

    from config.settings import AzureSQLConfig

    with patch.dict(
        os.environ,
        {
            "AZURE_SQL_SERVER": "test-server.database.windows.net",
            "AZURE_SQL_DATABASE": "test_db",
            "AZURE_SQL_USERNAME": "test_user",
            "AZURE_SQL_PASSWORD": "test_password",
            "AZURE_SQL_PORT": "1433",
        },
    ):
        return AzureSQLConfig()


@pytest.fixture
def mock_databricks_config():
    """
    Fixture providing a mock Databricks configuration.

    Returns:
        DatabricksConfig instance with test values
    """
    from unittest.mock import patch

    from config.settings import DatabricksConfig

    with patch.dict(
        os.environ,
        {
            "DATABRICKS_HOST": "https://test.azuredatabricks.net",
            "DATABRICKS_TOKEN": "dapi_test_token",
            "DATABRICKS_CLUSTER_ID": "test-cluster-123",
            "DATABRICKS_JOB_ID": "123456",
            "DATABRICKS_NOTEBOOK_PATH": "/test/notebook",
        },
    ):
        return DatabricksConfig()


@pytest.fixture
def sample_brewery_entity():
    """
    Fixture providing a sample Brewery entity for testing.

    Returns:
        Brewery entity
    """
    from domain import Address, Brewery, BreweryType, Contact, Coordinates, Location

    coords = Coordinates(latitude=37.7749, longitude=-122.4194)
    address = Address(
        street="123 Main St",
        city="San Francisco",
        state="California",
        postal_code="94102",
    )
    location = Location(coordinates=coords, address=address)
    contact = Contact(
        phone="555-1234",
        website_url="https://testbrewery.com",
        email="info@testbrewery.com",
    )

    return Brewery(
        id="test-brewery-1",
        name="Test Brewery",
        brewery_type=BreweryType.MICRO,
        location=location,
        contact=contact,
    )


@pytest.fixture
def sample_raw_brewery_dict():
    """
    Fixture providing raw brewery dictionary (API format).

    Returns:
        Dictionary with brewery data
    """
    return {
        "id": "raw-brewery-1",
        "name": "Raw Test Brewery",
        "brewery_type": "micro",
        "address_1": "456 Oak Ave",
        "address_2": None,
        "address_3": None,
        "city": "Los Angeles",
        "state_province": "California",
        "postal_code": "90001",
        "country": "United States",
        "longitude": "-118.2437",
        "latitude": "34.0522",
        "phone": "555-5678",
        "website_url": "https://rawtest.com",
        "state": "California",
        "street": "456 Oak Ave",
        "updated_at": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def in_memory_repository():
    """
    Fixture providing a fresh InMemoryBreweryRepository.

    Returns:
        InMemoryBreweryRepository instance
    """
    from repositories import InMemoryBreweryRepository

    return InMemoryBreweryRepository()


# Pytest configuration
def pytest_configure(config):
    """
    Pytest configuration hook.

    Registers custom markers.
    """
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "slow: mark test as slow")
    config.addinivalue_line("markers", "e2e: mark test as end-to-end test")
