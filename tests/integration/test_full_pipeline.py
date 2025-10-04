"""
E2E Integration Tests - Full ETL Pipeline

Tests the complete brewery ETL pipeline from extraction to loading.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict, Any

from use_cases import (
    ExtractBreweriesUseCase,
    TransformBreweriesUseCase,
    LoadBreweriesUseCase,
    ValidateBreweriesQualityUseCase,
)
from repositories import InMemoryBreweryRepository
from data_quality.rules import create_brewery_quality_engine
from config import APIConfig
from exceptions import ExtractionError, TransformationError, ValidationError


class TestFullETLPipeline:
    """Test complete ETL pipeline end-to-end."""

    @pytest.fixture
    def sample_api_response(self) -> List[Dict[str, Any]]:
        """Sample API response for testing."""
        return [
            {
                "id": "brewery-1",
                "name": "Test Brewery 1",
                "brewery_type": "micro",
                "address_1": "123 Main St",
                "address_2": None,
                "address_3": None,
                "city": "San Francisco",
                "state_province": "California",
                "postal_code": "94102",
                "country": "United States",
                "longitude": "-122.4194",
                "latitude": "37.7749",
                "phone": "555-1234",
                "website_url": "https://testbrewery1.com",
                "state": "California",
                "street": "123 Main St",
                "updated_at": "2024-01-01T00:00:00Z",
            },
            {
                "id": "brewery-2",
                "name": "Test Brewery 2",
                "brewery_type": "nano",
                "address_1": "456 Oak Ave",
                "city": "Los Angeles",
                "state_province": "California",
                "postal_code": "90001",
                "country": "United States",
                "longitude": "-118.2437",
                "latitude": "34.0522",
                "phone": None,
                "website_url": None,
                "state": "California",
                "street": "456 Oak Ave",
                "updated_at": "2024-01-02T00:00:00Z",
            },
        ]

    @pytest.fixture
    def mock_extractor(self, sample_api_response):
        """Mock data extractor."""
        extractor = Mock()
        extractor.extract.return_value = sample_api_response
        return extractor

    def test_full_pipeline_success(self, mock_extractor, sample_api_response):
        """Test complete pipeline: Extract → Transform → Load → Validate."""
        # 1. EXTRACT
        extract_uc = ExtractBreweriesUseCase(mock_extractor)
        raw_data = extract_uc.execute()

        assert len(raw_data) == 2
        assert raw_data[0]["id"] == "brewery-1"
        assert raw_data[1]["id"] == "brewery-2"

        # 2. TRANSFORM
        transform_uc = TransformBreweriesUseCase()
        breweries = transform_uc.execute(raw_data)

        assert len(breweries) == 2
        assert breweries[0].id == "brewery-1"
        assert breweries[0].name == "Test Brewery 1"
        assert breweries[0].brewery_type.value == "micro"
        assert breweries[1].id == "brewery-2"

        # 3. VALIDATE QUALITY
        engine = create_brewery_quality_engine(strict_mode=False)
        quality_uc = ValidateBreweriesQualityUseCase(engine)
        report = quality_uc.execute(breweries)

        assert report.is_overall_passed()
        assert report.overall_status in ["PASSED", "DEGRADED"]

        # 4. LOAD
        repository = InMemoryBreweryRepository()
        load_uc = LoadBreweriesUseCase(repository)
        loaded_count = load_uc.execute(breweries, min_quality=0.5)

        assert loaded_count == 2
        assert repository.count() == 2

        # 5. VERIFY DATA IN REPOSITORY
        brewery_1 = repository.get_by_id("brewery-1")
        assert brewery_1 is not None
        assert brewery_1.name == "Test Brewery 1"
        assert brewery_1.brewery_type.value == "micro"

        brewery_2 = repository.get_by_id("brewery-2")
        assert brewery_2 is not None
        assert brewery_2.name == "Test Brewery 2"

    def test_pipeline_with_extraction_failure(self, mock_extractor):
        """Test pipeline handles extraction failures gracefully."""
        mock_extractor.extract.side_effect = Exception("API unavailable")

        extract_uc = ExtractBreweriesUseCase(mock_extractor)

        with pytest.raises(ExtractionError) as exc_info:
            extract_uc.execute()

        assert "Failed to extract data" in str(exc_info.value)

    def test_pipeline_with_invalid_data(self, mock_extractor):
        """Test pipeline handles invalid data during transformation."""
        # Invalid data (missing required fields)
        invalid_data = [
            {
                "id": "invalid-1",
                # Missing 'name' - required field
                "brewery_type": "micro",
            }
        ]
        mock_extractor.extract.return_value = invalid_data

        extract_uc = ExtractBreweriesUseCase(mock_extractor)
        raw_data = extract_uc.execute()

        transform_uc = TransformBreweriesUseCase()

        # Should not raise, but skip invalid records
        breweries = transform_uc.execute(raw_data)
        assert len(breweries) == 0  # Invalid record skipped

    def test_pipeline_with_quality_filtering(self, mock_extractor, sample_api_response):
        """Test pipeline filters low-quality data."""
        # Add low-quality record (missing many fields)
        low_quality_record = {
            "id": "low-quality",
            "name": "Low Quality Brewery",
            "brewery_type": "micro",
            # Missing most fields
        }
        sample_api_response.append(low_quality_record)
        mock_extractor.extract.return_value = sample_api_response

        # Extract and Transform
        extract_uc = ExtractBreweriesUseCase(mock_extractor)
        raw_data = extract_uc.execute()

        transform_uc = TransformBreweriesUseCase()
        breweries = transform_uc.execute(raw_data)

        # Load with high quality threshold
        repository = InMemoryBreweryRepository()
        load_uc = LoadBreweriesUseCase(repository)
        loaded_count = load_uc.execute(breweries, min_quality=0.7)

        # Only high-quality records loaded
        assert loaded_count <= 2  # Low quality might be filtered
        assert repository.count() == loaded_count

    def test_pipeline_with_duplicate_handling(
        self, mock_extractor, sample_api_response
    ):
        """Test pipeline handles duplicate IDs."""
        # Add duplicate
        sample_api_response.append(sample_api_response[0].copy())
        mock_extractor.extract.return_value = sample_api_response

        # Extract and Transform
        extract_uc = ExtractBreweriesUseCase(mock_extractor)
        raw_data = extract_uc.execute()

        transform_uc = TransformBreweriesUseCase()
        breweries = transform_uc.execute(raw_data)

        # Load
        repository = InMemoryBreweryRepository()
        load_uc = LoadBreweriesUseCase(repository)
        loaded_count = load_uc.execute(breweries)

        # Duplicates should be handled (update instead of insert)
        assert repository.count() == 2  # Only 2 unique IDs

    @patch("services.brewery_api_extractor.requests")
    def test_pipeline_with_real_api_extractor(self, mock_requests, sample_api_response):
        """Test pipeline with real API extractor (mocked requests)."""
        # Mock HTTP response
        mock_response = Mock()
        mock_response.json.return_value = sample_api_response
        mock_response.raise_for_status = Mock()
        mock_requests.Session.return_value.get.return_value = mock_response

        # Use real extractor (but with mocked requests)
        from services import BreweryAPIExtractor
        from config import APIConfig

        api_config = APIConfig()
        extractor = BreweryAPIExtractor(api_config)

        # Run pipeline
        extract_uc = ExtractBreweriesUseCase(extractor)
        raw_data = extract_uc.execute()

        assert len(raw_data) == 2
        assert raw_data[0]["id"] == "brewery-1"

    def test_pipeline_metrics_collection(self, mock_extractor, sample_api_response):
        """Test pipeline collects observability metrics."""
        from observability import MetricsCollector

        # Extract
        extract_uc = ExtractBreweriesUseCase(mock_extractor)
        raw_data = extract_uc.execute()

        # Transform
        transform_uc = TransformBreweriesUseCase()
        breweries = transform_uc.execute(raw_data)

        # Collect metrics
        collector = MetricsCollector()
        metrics = collector.collect_data_metrics(
            data=raw_data, source="Open Brewery API", stage="extraction"
        )

        assert metrics.volume == 2
        assert metrics.source == "Open Brewery API"
        assert metrics.stage == "extraction"
        assert metrics.processing_time >= 0
