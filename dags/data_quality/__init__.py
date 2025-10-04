"""
Data Quality Framework - Enterprise Grade

Implements comprehensive data quality checks following industry standards.

Quality Dimensions (ISO 8000):
- Completeness: Are all required fields present?
- Accuracy: Are values correct and valid?
- Consistency: Do values follow business rules?
- Timeliness: Is data fresh and up-to-date?
- Validity: Does data conform to schema?
- Uniqueness: Are there duplicates?

Architecture:
- Framework: Core engine for running checks
- Dimensions: Individual quality dimension implementations
- Rules: Business-specific validation rules
- Reports: Quality score calculation and reporting

Usage:
    from data_quality import DataQualityEngine, CompletenessCheck

    engine = DataQualityEngine()
    engine.add_check(CompletenessCheck(['id', 'name']))

    results = engine.run_checks(data)
    if results['overall_score'] < 0.95:
        raise DataQualityException("Quality below threshold")

See Also:
    - data_quality_check_dag.py: DAG that uses this framework
    - rules/brewery_rules.py: Brewery-specific rules
"""

from .framework import (
    DataQualityEngine,
    DataQualityCheck,
    DataQualityDimension,
    DataQualityResult,
    DataQualityReport,
)

from .dimensions import (
    CompletenessCheck,
    AccuracyCheck,
    ConsistencyCheck,
    TimelinessCheck,
    ValidityCheck,
    UniquenessCheck,
)


__all__ = [
    # Core
    "DataQualityEngine",
    "DataQualityCheck",
    "DataQualityDimension",
    "DataQualityResult",
    "DataQualityReport",
    # Dimensions
    "CompletenessCheck",
    "AccuracyCheck",
    "ConsistencyCheck",
    "TimelinessCheck",
    "ValidityCheck",
    "UniquenessCheck",
]


__version__ = "1.0.0"
