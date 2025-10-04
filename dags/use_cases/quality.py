"""
Quality Use Cases - Data Quality Validation

Application-level logic for data quality checks.
"""

from typing import List, Dict, Any
from domain import Brewery, BreweryAggregate, BreweryValidator
from utils import get_logger


class ValidateBreweriesQualityUseCase:
    """
    Validate brewery data quality.

    Use Case: Check data quality and generate quality report.

    Responsibilities:
    - Validate each brewery
    - Calculate quality metrics
    - Generate quality report
    - Log quality issues

    Example:
        >>> use_case = ValidateBreweriesQualityUseCase()
        >>> report = use_case.execute(breweries)
        >>> print(f"Avg quality: {report['avg_quality_score']:.2%}")
    """

    def __init__(self, min_quality_threshold: float = 0.7):
        """
        Initialize use case.

        Args:
            min_quality_threshold: Minimum acceptable quality score (0.0 to 1.0)
        """
        self.min_quality_threshold = min_quality_threshold
        self.logger = get_logger(__name__)

    def execute(self, breweries: List[Brewery]) -> Dict[str, Any]:
        """
        Execute quality validation use case.

        Args:
            breweries: List of Brewery entities to validate

        Returns:
            Quality report dictionary

        Example:
            >>> report = use_case.execute(breweries)
            >>> if not report['passed']:
            ...     print(f"Quality issues: {report['issues']}")
        """
        self.logger.info(
            f"Starting quality validation of {len(breweries)} breweries "
            f"(threshold={self.min_quality_threshold})"
        )

        if not breweries:
            return self._empty_report()

        quality_scores = []
        issues = []
        warnings = []

        # Validate each brewery
        for brewery in breweries:
            aggregate = BreweryAggregate(brewery)
            aggregate.validate_consistency()

            quality_score = aggregate.get_quality_score()
            quality_scores.append(quality_score)

            # Check threshold
            if quality_score < self.min_quality_threshold:
                issues.append(
                    {
                        "brewery_id": brewery.id,
                        "brewery_name": brewery.name,
                        "quality_score": quality_score,
                        "errors": aggregate.validation_errors,
                        "warnings": aggregate.warnings,
                    }
                )

            # Collect warnings even if passed
            if aggregate.warnings:
                warnings.extend(
                    [
                        {
                            "brewery_id": brewery.id,
                            "brewery_name": brewery.name,
                            "warning": warning,
                        }
                        for warning in aggregate.warnings
                    ]
                )

        # Calculate metrics
        avg_quality = sum(quality_scores) / len(quality_scores)
        min_quality = min(quality_scores)
        max_quality = max(quality_scores)

        passed_count = sum(
            1 for score in quality_scores if score >= self.min_quality_threshold
        )

        failed_count = len(breweries) - passed_count
        passed = failed_count == 0

        report = {
            "passed": passed,
            "total_breweries": len(breweries),
            "passed_count": passed_count,
            "failed_count": failed_count,
            "avg_quality_score": avg_quality,
            "min_quality_score": min_quality,
            "max_quality_score": max_quality,
            "quality_threshold": self.min_quality_threshold,
            "issues": issues,
            "warnings": warnings,
            "quality_distribution": self._calculate_distribution(quality_scores),
        }

        # Log results
        if passed:
            self.logger.info(
                f"✅ Quality validation PASSED: "
                f"{passed_count}/{len(breweries)} breweries "
                f"(avg={avg_quality:.2%})"
            )
        else:
            self.logger.warning(
                f"❌ Quality validation FAILED: "
                f"{failed_count}/{len(breweries)} breweries below threshold "
                f"(avg={avg_quality:.2%}, threshold={self.min_quality_threshold:.2%})"
            )

        if warnings:
            self.logger.info(f"⚠️  {len(warnings)} warnings detected")

        return report

    def _calculate_distribution(self, quality_scores: List[float]) -> Dict[str, Any]:
        """Calculate quality score distribution."""
        return {
            "excellent": sum(1 for s in quality_scores if s >= 0.9),
            "good": sum(1 for s in quality_scores if 0.7 <= s < 0.9),
            "fair": sum(1 for s in quality_scores if 0.5 <= s < 0.7),
            "poor": sum(1 for s in quality_scores if s < 0.5),
        }

    def _empty_report(self) -> Dict[str, Any]:
        """Generate empty report for no data."""
        return {
            "passed": True,
            "total_breweries": 0,
            "passed_count": 0,
            "failed_count": 0,
            "avg_quality_score": 0.0,
            "min_quality_score": 0.0,
            "max_quality_score": 0.0,
            "quality_threshold": self.min_quality_threshold,
            "issues": [],
            "warnings": [],
            "quality_distribution": {
                "excellent": 0,
                "good": 0,
                "fair": 0,
                "poor": 0,
            },
        }

    def execute_detailed_validation(self, breweries: List[Brewery]) -> Dict[str, Any]:
        """
        Execute detailed validation with per-brewery analysis.

        Args:
            breweries: List of Brewery entities

        Returns:
            Detailed quality report with per-brewery metrics
        """
        self.logger.info(
            f"Starting detailed quality validation of {len(breweries)} breweries"
        )

        brewery_reports = []

        for brewery in breweries:
            validator = BreweryValidator()

            # Completeness check
            completeness = validator.validate_completeness(brewery)

            # Processing validation
            can_process, processing_errors = validator.validate_for_processing(brewery)

            # Export validation
            can_export, export_errors = validator.validate_for_export(brewery)

            # Quality score
            quality_score = validator.calculate_quality_score(brewery)

            brewery_reports.append(
                {
                    "brewery_id": brewery.id,
                    "brewery_name": brewery.name,
                    "brewery_type": str(brewery.brewery_type),
                    "quality_score": quality_score,
                    "completeness": completeness,
                    "can_process": can_process,
                    "processing_errors": processing_errors,
                    "can_export": can_export,
                    "export_errors": export_errors,
                    "is_active": brewery.is_active(),
                    "is_craft": brewery.is_craft(),
                    "has_location": brewery.has_location(),
                    "has_contact": brewery.has_contact(),
                    "has_coordinates": brewery.has_coordinates(),
                }
            )

        # Generate summary
        avg_quality = (
            sum(r["quality_score"] for r in brewery_reports) / len(brewery_reports)
            if brewery_reports
            else 0.0
        )

        can_process_count = sum(1 for r in brewery_reports if r["can_process"])
        can_export_count = sum(1 for r in brewery_reports if r["can_export"])

        return {
            "summary": {
                "total_breweries": len(breweries),
                "avg_quality_score": avg_quality,
                "can_process_count": can_process_count,
                "can_export_count": can_export_count,
                "active_count": sum(1 for r in brewery_reports if r["is_active"]),
                "craft_count": sum(1 for r in brewery_reports if r["is_craft"]),
            },
            "brewery_reports": brewery_reports,
        }
