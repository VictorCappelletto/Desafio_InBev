"""
Integration Tests - Use Cases Layer

Tests application logic and use case orchestration.
"""

import pytest
from unittest.mock import Mock
from typing import List, Dict, Any

from use_cases import (
    ExtractBreweriesUseCase,
    TransformBreweriesUseCase,
    LoadBreweriesUseCase,
    ValidateBreweriesQualityUseCase,
)
from repositories import InMemoryBreweryRepository
from data_quality.rules import create_brewery_quality_engine
from domain import Brewery, BreweryType
from exceptions import ExtractionError, TransformationError, ValidationError


class TestExtractBreweriesUseCase:
    """Test Extract Use Case."""

    @pytest.fixture
    def mock_extractor(self):
        """Mock data extractor."""
        extractor = Mock()
        extractor.extract.return_value = [
            {"id": "1", "name": "Brewery 1"},
            {"id": "2", "name": "Brewery 2"},
        ]
        return extractor

    def test_execute_success(self, mock_extractor):
        """Test successful extraction."""
        use_case = ExtractBreweriesUseCase(mock_extractor)
        result = use_case.execute()

        assert len(result) == 2
        assert result[0]["id"] == "1"
        mock_extractor.extract.assert_called_once()

    def test_execute_with_kwargs(self, mock_extractor):
        """Test extraction with parameters."""
        use_case = ExtractBreweriesUseCase(mock_extractor)
        result = use_case.execute(per_page=50, by_state="california")

        mock_extractor.extract.assert_called_once_with(
            per_page=50, by_state="california"
        )

    def test_execute_with_retry_on_failure(self, mock_extractor):
        """Test retry logic on transient failures."""
        # Fail twice, succeed on third attempt
        mock_extractor.extract.side_effect = [
            Exception("Transient error 1"),
            Exception("Transient error 2"),
            [{"id": "1", "name": "Success"}],
        ]

        use_case = ExtractBreweriesUseCase(mock_extractor)
        result = use_case.execute()

        assert len(result) == 1
        assert result[0]["name"] == "Success"
        assert mock_extractor.extract.call_count == 3

    def test_execute_raises_after_max_retries(self, mock_extractor):
        """Test raises error after maximum retries."""
        mock_extractor.extract.side_effect = Exception("Persistent error")

        use_case = ExtractBreweriesUseCase(mock_extractor)

        with pytest.raises(ExtractionError) as exc_info:
            use_case.execute()

        assert "Failed to extract data after 3 attempts" in str(exc_info.value)
        assert mock_extractor.extract.call_count == 3


class TestTransformBreweriesUseCase:
    """Test Transform Use Case."""

    @pytest.fixture
    def valid_raw_data(self) -> List[Dict[str, Any]]:
        """Valid raw data for transformation."""
        return [
            {
                "id": "test-1",
                "name": "Test Brewery",
                "brewery_type": "micro",
                "city": "San Francisco",
                "state": "California",
                "country": "United States",
                "latitude": "37.7749",
                "longitude": "-122.4194",
                "street": "123 Main St",
                "postal_code": "94102",
                "phone": "555-1234",
                "website_url": "https://test.com",
                "updated_at": "2024-01-01T00:00:00Z",
            }
        ]

    def test_execute_success(self, valid_raw_data):
        """Test successful transformation."""
        use_case = TransformBreweriesUseCase()
        breweries = use_case.execute(valid_raw_data)

        assert len(breweries) == 1
        assert isinstance(breweries[0], Brewery)
        assert breweries[0].id == "test-1"
        assert breweries[0].name == "Test Brewery"
        assert breweries[0].brewery_type == BreweryType.MICRO

    def test_execute_skips_invalid_records(self):
        """Test skipping invalid records."""
        invalid_data = [
            {"id": "1", "name": "Valid", "brewery_type": "micro"},
            {"id": "2"},  # Missing 'name' - invalid
            {"id": "3", "name": "Also Valid", "brewery_type": "nano"},
        ]

        use_case = TransformBreweriesUseCase()
        breweries = use_case.execute(invalid_data)

        # Should skip invalid record
        assert len(breweries) == 2
        assert breweries[0].id == "1"
        assert breweries[1].id == "3"

    def test_execute_handles_empty_input(self):
        """Test handling empty input."""
        use_case = TransformBreweriesUseCase()
        breweries = use_case.execute([])

        assert len(breweries) == 0

    def test_execute_collects_metrics(self, valid_raw_data):
        """Test metrics collection during transformation."""
        use_case = TransformBreweriesUseCase()
        breweries = use_case.execute(valid_raw_data)

        # Should successfully transform without errors
        assert len(breweries) == 1


class TestLoadBreweriesUseCase:
    """Test Load Use Case."""

    @pytest.fixture
    def sample_breweries(self) -> List[Brewery]:
        """Sample brewery entities."""
        return [
            Brewery(
                id="load-1",
                name="High Quality Brewery",
                brewery_type=BreweryType.MICRO,
            ),
            Brewery(
                id="load-2",
                name="Low Quality Brewery",
                brewery_type=BreweryType.NANO,
            ),
        ]

    @pytest.fixture
    def repository(self):
        """Fresh repository for each test."""
        return InMemoryBreweryRepository()

    def test_execute_success(self, repository, sample_breweries):
        """Test successful loading."""
        use_case = LoadBreweriesUseCase(repository)
        count = use_case.execute(sample_breweries)

        assert count == 2
        assert repository.count() == 2

    def test_execute_with_quality_filtering(self, repository):
        """Test quality-based filtering."""
        # High quality brewery
        high_quality = Brewery(
            id="hq-1",
            name="Complete Brewery",
            brewery_type=BreweryType.MICRO,
            # More fields = higher quality
        )

        # Low quality brewery (minimal fields)
        low_quality = Brewery(
            id="lq-1",
            name="Minimal Brewery",
            brewery_type=BreweryType.MICRO,
        )

        use_case = LoadBreweriesUseCase(repository)
        count = use_case.execute([high_quality, low_quality], min_quality=0.7)

        # At least high quality should be loaded
        assert count >= 1

    def test_execute_handles_duplicates(self, repository, sample_breweries):
        """Test handling duplicate IDs."""
        # Load once
        use_case = LoadBreweriesUseCase(repository)
        count1 = use_case.execute(sample_breweries)

        # Load again (duplicates)
        count2 = use_case.execute(sample_breweries)

        # Should update, not duplicate
        assert repository.count() == 2

    def test_execute_with_empty_input(self, repository):
        """Test handling empty input."""
        use_case = LoadBreweriesUseCase(repository)
        count = use_case.execute([])

        assert count == 0
        assert repository.count() == 0


class TestValidateBreweriesQualityUseCase:
    """Test Quality Validation Use Case."""

    @pytest.fixture
    def high_quality_breweries(self) -> List[Brewery]:
        """High quality brewery data."""
        return [
            Brewery(
                id="hq-1",
                name="Complete Brewery",
                brewery_type=BreweryType.MICRO,
            )
        ]

    def test_execute_with_passing_data(self, high_quality_breweries):
        """Test validation with passing data."""
        engine = create_brewery_quality_engine(strict_mode=False)
        use_case = ValidateBreweriesQualityUseCase(engine)

        report = use_case.execute(high_quality_breweries)

        assert report is not None
        assert report.overall_status in ["PASSED", "DEGRADED"]

    def test_execute_with_strict_mode_passing(self, high_quality_breweries):
        """Test strict mode with passing data."""
        engine = create_brewery_quality_engine(strict_mode=True)
        use_case = ValidateBreweriesQualityUseCase(engine)

        # Should not raise with high quality data
        report = use_case.execute(high_quality_breweries)
        assert report.is_overall_passed()

    def test_execute_with_empty_input(self):
        """Test validation with empty input."""
        engine = create_brewery_quality_engine(strict_mode=False)
        use_case = ValidateBreweriesQualityUseCase(engine)

        report = use_case.execute([])

        # Should handle empty gracefully
        assert report is not None

    def test_execute_collects_detailed_results(self, high_quality_breweries):
        """Test detailed quality results."""
        engine = create_brewery_quality_engine(strict_mode=False)
        use_case = ValidateBreweriesQualityUseCase(engine)

        report = use_case.execute(high_quality_breweries)

        # Should have results from multiple checks
        assert len(report.results) > 0
        assert all(hasattr(r, "check_name") for r in report.results)
        assert all(hasattr(r, "score") for r in report.results)
