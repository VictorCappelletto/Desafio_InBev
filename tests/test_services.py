"""
Unit Tests for Services

Tests the service classes (extractors, loaders, transformers).
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add dags to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'dags'))

from config.settings import APIConfig, AzureSQLConfig
from services.brewery_api_extractor import BreweryAPIExtractor
from services.brewery_transformer import BreweryTransformer
from exceptions import ExtractionError, ValidationError


class TestBreweryAPIExtractor:
    """Test BreweryAPIExtractor service."""
    
    def test_initialization(self):
        """Test extractor initialization."""
        config = APIConfig()
        extractor = BreweryAPIExtractor(config)
        
        assert extractor.config == config
        assert extractor._session is not None
    
    @patch('services.brewery_api_extractor.requests.Session')
    def test_extract_success(self, mock_session):
        """Test successful data extraction."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = [
            {'id': '1', 'name': 'Test Brewery', 'brewery_type': 'micro'}
        ]
        mock_response.status_code = 200
        
        mock_session_instance = Mock()
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        config = APIConfig()
        extractor = BreweryAPIExtractor(config)
        extractor._session = mock_session_instance
        
        # Extract
        data = extractor.extract()
        
        assert len(data) == 1
        assert data[0]['name'] == 'Test Brewery'
    
    def test_validate_data_valid(self):
        """Test data validation with valid data."""
        config = APIConfig()
        extractor = BreweryAPIExtractor(config)
        
        valid_data = [
            {'id': '1', 'name': 'Brewery 1', 'brewery_type': 'micro'},
            {'id': '2', 'name': 'Brewery 2', 'brewery_type': 'regional'}
        ]
        
        assert extractor.validate_data(valid_data) is True
    
    def test_validate_data_missing_field(self):
        """Test validation fails with missing required field."""
        config = APIConfig()
        extractor = BreweryAPIExtractor(config)
        
        invalid_data = [
            {'id': '1', 'name': 'Brewery 1'}  # Missing brewery_type
        ]
        
        assert extractor.validate_data(invalid_data) is False
    
    def test_validate_data_not_list(self):
        """Test validation fails if data is not a list."""
        config = APIConfig()
        extractor = BreweryAPIExtractor(config)
        
        invalid_data = {'id': '1', 'name': 'Brewery 1'}  # Not a list
        
        assert extractor.validate_data(invalid_data) is False
    
    def test_validate_data_empty_list(self):
        """Test validation passes with empty list."""
        config = APIConfig()
        extractor = BreweryAPIExtractor(config)
        
        empty_data = []
        
        assert extractor.validate_data(empty_data) is True


class TestBreweryTransformer:
    """Test BreweryTransformer service."""
    
    def test_initialization(self):
        """Test transformer initialization."""
        transformer = BreweryTransformer()
        
        assert transformer is not None
    
    def test_transform_success(self):
        """Test successful data transformation."""
        transformer = BreweryTransformer()
        
        raw_data = [
            {
                'id': '1',
                'name': 'Test Brewery',
                'brewery_type': 'micro',
                'city': 'San Francisco',
                'state': 'California',
                'longitude': -122.4194,
                'latitude': 37.7749
            }
        ]
        
        transformed = transformer.transform(raw_data)
        
        assert len(transformed) == 1
        assert transformed[0]['id'] == '1'
        assert transformed[0]['name'] == 'Test Brewery'
        assert isinstance(transformed[0]['longitude'], float)
    
    def test_transform_empty_list(self):
        """Test transformation with empty list."""
        transformer = BreweryTransformer()
        
        transformed = transformer.transform([])
        
        assert transformed == []
    
    def test_safe_string_truncation(self):
        """Test string truncation."""
        transformer = BreweryTransformer()
        
        long_string = "A" * 300
        truncated = transformer._safe_string(long_string, max_length=100)
        
        assert len(truncated) == 100
    
    def test_safe_string_none(self):
        """Test safe_string with None value."""
        transformer = BreweryTransformer()
        
        result = transformer._safe_string(None)
        
        assert result is None
    
    def test_safe_float_valid(self):
        """Test safe_float with valid value."""
        transformer = BreweryTransformer()
        
        assert transformer._safe_float(42.5) == 42.5
        assert transformer._safe_float("42.5") == 42.5
    
    def test_safe_float_invalid(self):
        """Test safe_float with invalid value."""
        transformer = BreweryTransformer()
        
        assert transformer._safe_float("invalid") is None
        assert transformer._safe_float(None) is None


class TestFactories:
    """Test factory classes."""
    
    def test_etl_factory_import(self):
        """Test that ETLFactory can be imported."""
        from factories.etl_factory import ETLFactory
        
        assert ETLFactory is not None
    
    def test_create_brewery_extractor(self):
        """Test brewery extractor creation."""
        from factories.etl_factory import ETLFactory
        
        extractor = ETLFactory.create_brewery_extractor()
        
        assert extractor is not None
        assert hasattr(extractor, 'extract')
    
    def test_create_brewery_transformer(self):
        """Test brewery transformer creation."""
        from factories.etl_factory import ETLFactory
        
        transformer = ETLFactory.create_brewery_transformer()
        
        assert transformer is not None
        assert hasattr(transformer, 'transform')
    
    def test_create_etl_pipeline(self):
        """Test complete ETL pipeline creation."""
        from factories.etl_factory import ETLFactory
        
        extractor, transformer, loader = ETLFactory.create_etl_pipeline()
        
        assert extractor is not None
        assert transformer is not None
        assert loader is not None


class TestExceptions:
    """Test custom exceptions."""
    
    def test_extraction_error(self):
        """Test ExtractionError."""
        error = ExtractionError(
            "Failed to extract",
            details={"url": "http://test.com"}
        )
        
        assert str(error) == "Failed to extract | Details: url=http://test.com"
    
    def test_validation_error(self):
        """Test ValidationError."""
        error = ValidationError("Validation failed")
        
        assert "Validation failed" in str(error)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

