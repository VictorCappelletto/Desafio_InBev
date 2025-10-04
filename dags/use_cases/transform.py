"""
Transform Use Cases - Data Transformation Logic

Application-level logic for transforming brewery data.
"""

from typing import List, Dict, Any
from domain import Brewery, BreweryAggregate
from utils import get_logger


class TransformBreweriesUseCase:
    """
    Transform raw data into domain entities.

    Use Case: Convert raw dictionaries into validated Brewery entities.

    Responsibilities:
    - Parse raw data
    - Create domain entities
    - Validate business rules
    - Handle transformation errors
    - Return domain entities

    Example:
        >>> use_case = TransformBreweriesUseCase()
        >>> raw_data = [{"id": "1", "name": "Brewery A", ...}]
        >>> breweries = use_case.execute(raw_data)
        >>> print(f"Transformed {len(breweries)} breweries")
    """

    def __init__(self, strict_mode: bool = False):
        """
        Initialize use case.

        Args:
            strict_mode: If True, fail on any validation error.
                        If False, skip invalid records and continue.
        """
        self.strict_mode = strict_mode
        self.logger = get_logger(__name__)

    def execute(self, raw_data: List[Dict[str, Any]]) -> List[Brewery]:
        """
        Execute transformation use case.

        Args:
            raw_data: List of raw brewery dictionaries

        Returns:
            List of validated Brewery entities

        Raises:
            TransformationError: If strict_mode=True and validation fails

        Example:
            >>> raw = [
            ...     {"id": "1", "name": "Brewery A", "brewery_type": "micro"},
            ...     {"id": "2", "name": "Brewery B", "brewery_type": "nano"}
            ... ]
            >>> breweries = use_case.execute(raw)
        """
        from exceptions import TransformationError

        self.logger.info(
            f"Starting transformation of {len(raw_data)} records "
            f"(strict_mode={self.strict_mode})"
        )

        breweries: List[Brewery] = []
        errors: List[Dict[str, Any]] = []

        for index, raw_record in enumerate(raw_data):
            try:
                # Convert to domain entity
                brewery = Brewery.from_dict(raw_record)

                # Validate (happens automatically in __post_init__)
                # But we also validate aggregate
                aggregate = BreweryAggregate(brewery)
                if not aggregate.validate_consistency():
                    if self.strict_mode:
                        raise TransformationError(
                            f"Validation failed for record {index}",
                            details={
                                "errors": aggregate.validation_errors,
                                "warnings": aggregate.warnings,
                            },
                        )
                    else:
                        self.logger.warning(
                            f"Record {index} has validation errors: "
                            f"{aggregate.validation_errors}"
                        )
                        errors.append(
                            {
                                "index": index,
                                "record": raw_record,
                                "errors": aggregate.validation_errors,
                            }
                        )
                        continue

                breweries.append(brewery)

            except Exception as e:
                error_detail = {
                    "index": index,
                    "record": raw_record,
                    "error": str(e),
                    "error_type": type(e).__name__,
                }

                if self.strict_mode:
                    raise TransformationError(
                        f"Failed to transform record {index}: {e}", details=error_detail
                    ) from e
                else:
                    self.logger.warning(f"Skipping record {index} due to error: {e}")
                    errors.append(error_detail)

        success_count = len(breweries)
        error_count = len(errors)
        success_rate = (success_count / len(raw_data) * 100) if raw_data else 0

        self.logger.info(
            f"Transformation complete: {success_count} success, "
            f"{error_count} errors ({success_rate:.1f}% success rate)"
        )

        if errors:
            self.logger.warning(f"Transformation errors: {error_count} records failed")

        return breweries

    def execute_with_quality_metrics(
        self, raw_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Execute transformation with quality metrics.

        Args:
            raw_data: List of raw brewery dictionaries

        Returns:
            Dictionary with breweries and metrics

        Example:
            >>> result = use_case.execute_with_quality_metrics(raw_data)
            >>> print(f"Avg quality: {result['avg_quality_score']:.2%}")
            >>> breweries = result['breweries']
        """
        breweries = self.execute(raw_data)

        # Calculate quality metrics
        quality_scores = []
        complete_count = 0
        active_count = 0
        craft_count = 0

        for brewery in breweries:
            aggregate = BreweryAggregate(brewery)
            quality_scores.append(aggregate.get_quality_score())

            if brewery.is_complete():
                complete_count += 1
            if brewery.is_active():
                active_count += 1
            if brewery.is_craft():
                craft_count += 1

        avg_quality = (
            sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
        )

        return {
            "breweries": breweries,
            "total_count": len(breweries),
            "avg_quality_score": avg_quality,
            "complete_count": complete_count,
            "active_count": active_count,
            "craft_count": craft_count,
            "quality_distribution": {
                "excellent": sum(1 for s in quality_scores if s >= 0.9),
                "good": sum(1 for s in quality_scores if 0.7 <= s < 0.9),
                "fair": sum(1 for s in quality_scores if 0.5 <= s < 0.7),
                "poor": sum(1 for s in quality_scores if s < 0.5),
            },
        }
