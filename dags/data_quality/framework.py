"""
Data Quality Framework - Core Engine

Implements the core data quality checking engine following enterprise patterns.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class DataQualityDimension(Enum):
    """
    Six dimensions of data quality based on ISO 8000 standard.

    Each dimension represents a different aspect of data quality that should
    be measured and monitored.
    """

    COMPLETENESS = "completeness"  # Are all required fields present?
    ACCURACY = "accuracy"  # Are values correct?
    CONSISTENCY = "consistency"  # Do values follow business rules?
    TIMELINESS = "timeliness"  # Is data fresh?
    VALIDITY = "validity"  # Does data conform to schema?
    UNIQUENESS = "uniqueness"  # Are there duplicates?


@dataclass
class DataQualityResult:
    """
    Result of a single data quality check.

    Attributes:
        dimension: Quality dimension checked
        score: Quality score (0.0 to 1.0)
        passed: Whether check passed threshold
        threshold: Minimum acceptable score
        details: Additional information about the check
        checked_at: Timestamp when check was performed
    """

    dimension: DataQualityDimension
    score: float
    passed: bool
    threshold: float
    details: Dict[str, Any] = field(default_factory=dict)
    checked_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate result values."""
        if not 0.0 <= self.score <= 1.0:
            raise ValueError(f"Score must be between 0 and 1, got {self.score}")
        if not 0.0 <= self.threshold <= 1.0:
            raise ValueError(f"Threshold must be between 0 and 1, got {self.threshold}")


@dataclass
class DataQualityReport:
    """
    Comprehensive report of all quality checks.

    Aggregates results from multiple checks and calculates overall quality score.

    Attributes:
        results: List of individual check results
        overall_score: Weighted average of all scores
        passed: Whether all checks passed
        total_records: Number of records checked
        generated_at: Report generation timestamp
    """

    results: List[DataQualityResult]
    overall_score: float
    passed: bool
    total_records: int
    generated_at: datetime = field(default_factory=datetime.now)

    @property
    def failed_checks(self) -> List[DataQualityResult]:
        """Return list of failed checks."""
        return [r for r in self.results if not r.passed]

    @property
    def passed_checks(self) -> List[DataQualityResult]:
        """Return list of passed checks."""
        return [r for r in self.results if r.passed]

    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary for serialization."""
        return {
            "overall_score": self.overall_score,
            "passed": self.passed,
            "total_records": self.total_records,
            "generated_at": self.generated_at.isoformat(),
            "summary": {
                "total_checks": len(self.results),
                "passed_checks": len(self.passed_checks),
                "failed_checks": len(self.failed_checks),
            },
            "results": [
                {
                    "dimension": r.dimension.value,
                    "score": r.score,
                    "passed": r.passed,
                    "threshold": r.threshold,
                    "details": r.details,
                    "checked_at": r.checked_at.isoformat(),
                }
                for r in self.results
            ],
        }


class DataQualityCheck(ABC):
    """
    Abstract base class for data quality checks.

    All quality checks must inherit from this class and implement the check method.

    Attributes:
        dimension: Quality dimension this check validates
        threshold: Minimum acceptable score (0.0 to 1.0)
        weight: Importance weight for overall score calculation

    Example:
        class CustomCheck(DataQualityCheck):
            def __init__(self):
                super().__init__(
                    dimension=DataQualityDimension.ACCURACY,
                    threshold=0.95,
                    weight=1.0
                )

            def check(self, data: List[Dict[str, Any]]) -> DataQualityResult:
                score = self._calculate_score(data)
                return DataQualityResult(
                    dimension=self.dimension,
                    score=score,
                    passed=score >= self.threshold,
                    threshold=self.threshold
                )
    """

    def __init__(
        self,
        dimension: DataQualityDimension,
        threshold: float = 0.95,
        weight: float = 1.0,
    ):
        """
        Initialize quality check.

        Args:
            dimension: Quality dimension to check
            threshold: Minimum acceptable score (default: 0.95)
            weight: Importance weight (default: 1.0)

        Raises:
            ValueError: If threshold or weight are out of valid range
        """
        if not 0.0 <= threshold <= 1.0:
            raise ValueError(f"Threshold must be between 0 and 1, got {threshold}")
        if weight < 0:
            raise ValueError(f"Weight must be non-negative, got {weight}")

        self.dimension = dimension
        self.threshold = threshold
        self.weight = weight
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def check(self, data: List[Dict[str, Any]]) -> DataQualityResult:
        """
        Perform data quality check.

        Args:
            data: List of records to check

        Returns:
            DataQualityResult with score and details

        Raises:
            Exception: If check fails to execute
        """
        pass

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"dimension={self.dimension.value}, "
            f"threshold={self.threshold}, "
            f"weight={self.weight})"
        )


class DataQualityEngine:
    """
    Core engine for running data quality checks.

    Orchestrates multiple quality checks and generates comprehensive reports.
    Implements Strategy pattern for flexible check composition.

    Example:
        # Create engine
        engine = DataQualityEngine()

        # Add checks
        engine.add_check(CompletenessCheck(['id', 'name']))
        engine.add_check(UniquenessCheck('id'))

        # Run all checks
        report = engine.run_checks(data)

        # Evaluate results
        if not report.passed:
            logger.error(f"Quality failed: {report.overall_score}")
            for failed in report.failed_checks:
                logger.error(f"  - {failed.dimension.value}: {failed.score}")
    """

    def __init__(self, min_overall_score: float = 0.95):
        """
        Initialize quality engine.

        Args:
            min_overall_score: Minimum acceptable overall score (default: 0.95)
        """
        self.checks: List[DataQualityCheck] = []
        self.min_overall_score = min_overall_score
        self.logger = logging.getLogger(__name__)

    def add_check(self, check: DataQualityCheck) -> "DataQualityEngine":
        """
        Add a quality check to the engine.

        Args:
            check: Quality check to add

        Returns:
            Self for method chaining

        Example:
            engine.add_check(check1).add_check(check2).add_check(check3)
        """
        self.checks.append(check)
        self.logger.info(f"Added check: {check}")
        return self

    def run_checks(self, data: List[Dict[str, Any]]) -> DataQualityReport:
        """
        Run all registered quality checks.

        Args:
            data: List of records to check

        Returns:
            DataQualityReport with all results and overall score

        Raises:
            ValueError: If no checks are registered or data is empty
        """
        if not self.checks:
            raise ValueError("No quality checks registered")

        if not data:
            raise ValueError("Cannot run quality checks on empty data")

        self.logger.info(
            f"Running {len(self.checks)} quality checks on {len(data)} records"
        )

        results: List[DataQualityResult] = []

        # Run each check
        for check in self.checks:
            try:
                self.logger.debug(f"Running check: {check.dimension.value}")
                result = check.check(data)
                results.append(result)

                status = "✅ PASSED" if result.passed else "❌ FAILED"
                self.logger.info(
                    f"{status} {check.dimension.value}: "
                    f"{result.score:.2%} (threshold: {result.threshold:.2%})"
                )

            except Exception as e:
                self.logger.error(
                    f"Check failed: {check.dimension.value}", exc_info=True
                )
                # Create failed result
                results.append(
                    DataQualityResult(
                        dimension=check.dimension,
                        score=0.0,
                        passed=False,
                        threshold=check.threshold,
                        details={"error": str(e)},
                    )
                )

        # Calculate overall score (weighted average)
        total_weight = sum(check.weight for check in self.checks)
        weighted_sum = sum(
            result.score * check.weight for result, check in zip(results, self.checks)
        )
        overall_score = weighted_sum / total_weight if total_weight > 0 else 0.0

        # Generate report
        report = DataQualityReport(
            results=results,
            overall_score=overall_score,
            passed=overall_score >= self.min_overall_score,
            total_records=len(data),
        )

        self.logger.info(
            f"Quality check complete: {overall_score:.2%} "
            f"({'PASSED' if report.passed else 'FAILED'})"
        )

        return report

    def clear_checks(self) -> None:
        """Remove all registered checks."""
        self.checks.clear()
        self.logger.info("Cleared all quality checks")

    def __repr__(self) -> str:
        return f"DataQualityEngine(checks={len(self.checks)}, min_score={self.min_overall_score})"
