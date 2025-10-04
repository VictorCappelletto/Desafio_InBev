"""
Extract Use Cases - Data Extraction Logic

Application-level logic for extracting brewery data.
"""

from typing import Any, Dict, List

from interfaces import IDataExtractor
from utils import get_logger


class ExtractBreweriesUseCase:
    """
    Extract breweries from external source.

    Use Case: Extract raw brewery data from API/file/database.

    Responsibilities:
    - Orchestrate extraction
    - Handle errors
    - Log extraction metrics
    - Return raw data

    Example:
        >>> from services import BreweryAPIExtractor
        >>> extractor = BreweryAPIExtractor(config)
        >>> use_case = ExtractBreweriesUseCase(extractor)
        >>> raw_data = use_case.execute(per_page=100, page=1)
        >>> print(f"Extracted {len(raw_data)} records")
    """

    def __init__(self, extractor: IDataExtractor):
        """
        Initialize use case.

        Args:
            extractor: Data extractor implementation (DIP: depends on interface)
        """
        self.extractor = extractor
        self.logger = get_logger(__name__)

    def execute(self, **extraction_params: Any) -> List[Dict[str, Any]]:
        """
        Execute extraction use case.

        Args:
            **extraction_params: Parameters for extraction (pagination, filters, etc.)

        Returns:
            List of raw brewery dictionaries

        Raises:
            ExtractionError: If extraction fails

        Example:
            >>> # Extract with pagination
            >>> data = use_case.execute(per_page=50, page=1)
            >>>
            >>> # Extract with filters
            >>> data = use_case.execute(by_city="portland", by_state="oregon")
        """
        self.logger.info(
            f"Starting brewery extraction with params: {extraction_params}"
        )

        # Delegate to extractor (Dependency Inversion)
        raw_data = self.extractor.extract(**extraction_params)

        self.logger.info(f"Extracted {len(raw_data)} raw brewery records")

        return raw_data

    def execute_with_retry(
        self, max_retries: int = 3, **extraction_params: Any
    ) -> List[Dict[str, Any]]:
        """
        Execute extraction with retry logic.

        Args:
            max_retries: Maximum number of retries
            **extraction_params: Parameters for extraction

        Returns:
            List of raw brewery dictionaries

        Raises:
            ExtractionError: If all retries fail
        """
        import time

        from exceptions import ExtractionError

        for attempt in range(1, max_retries + 1):
            try:
                self.logger.info(f"Extraction attempt {attempt}/{max_retries}")
                return self.execute(**extraction_params)

            except ExtractionError as e:
                if attempt == max_retries:
                    self.logger.error(f"All {max_retries} extraction attempts failed")
                    raise

                wait_time = 2**attempt  # Exponential backoff
                self.logger.warning(
                    f"Attempt {attempt} failed: {e}. " f"Retrying in {wait_time}s..."
                )
                time.sleep(wait_time)

        # Should never reach here
        raise ExtractionError("Unexpected error in retry logic")
