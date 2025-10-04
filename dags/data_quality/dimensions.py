"""
Data Quality Dimensions - Concrete Implementations

Implements the six dimensions of data quality based on ISO 8000 standard.
Each dimension has its own check class that can be configured and reused.
"""

from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Set

from .framework import DataQualityCheck, DataQualityDimension, DataQualityResult


class CompletenessCheck(DataQualityCheck):
    """
    Completeness: Checks if all required fields are present and non-null.

    Measures the percentage of required fields that have values across all records.

    Example:
        >>> check = CompletenessCheck(['id', 'name', 'brewery_type'])
        >>> result = check.check(data)
        >>> print(f"Completeness: {result.score:.2%}")
    """

    def __init__(
        self, required_fields: List[str], threshold: float = 0.95, weight: float = 1.0
    ):
        """
        Initialize completeness check.

        Args:
            required_fields: List of field names that must be present
            threshold: Minimum acceptable completeness (default: 0.95)
            weight: Importance weight (default: 1.0)
        """
        super().__init__(
            dimension=DataQualityDimension.COMPLETENESS,
            threshold=threshold,
            weight=weight,
        )
        self.required_fields = required_fields

    def check(self, data: List[Dict[str, Any]]) -> DataQualityResult:
        """
        Check data completeness.

        Args:
            data: List of records to check

        Returns:
            DataQualityResult with completeness score
        """
        if not data:
            return DataQualityResult(
                dimension=self.dimension,
                score=0.0,
                passed=False,
                threshold=self.threshold,
                details={"error": "Empty dataset"},
            )

        total_fields = len(data) * len(self.required_fields)
        filled_fields = 0
        missing_by_field = {field: 0 for field in self.required_fields}

        for record in data:
            for field in self.required_fields:
                value = record.get(field)
                if value is not None and value != "":
                    filled_fields += 1
                else:
                    missing_by_field[field] += 1

        score = filled_fields / total_fields if total_fields > 0 else 0.0

        return DataQualityResult(
            dimension=self.dimension,
            score=score,
            passed=score >= self.threshold,
            threshold=self.threshold,
            details={
                "total_fields_checked": total_fields,
                "filled_fields": filled_fields,
                "missing_fields": total_fields - filled_fields,
                "missing_by_field": missing_by_field,
                "completeness_percentage": f"{score:.2%}",
            },
        )


class AccuracyCheck(DataQualityCheck):
    """
    Accuracy: Checks if values conform to expected formats and ranges.

    Validates that field values match expected patterns, types, or ranges.

    Example:
        >>> validators = {
        ...     'brewery_type': lambda x: x in ['micro', 'nano', 'regional'],
        ...     'phone': lambda x: len(x) >= 10 if x else True
        ... }
        >>> check = AccuracyCheck(validators)
        >>> result = check.check(data)
    """

    def __init__(
        self,
        field_validators: Dict[str, Callable[[Any], bool]],
        threshold: float = 0.95,
        weight: float = 1.0,
    ):
        """
        Initialize accuracy check.

        Args:
            field_validators: Dict mapping field names to validation functions
            threshold: Minimum acceptable accuracy (default: 0.95)
            weight: Importance weight (default: 1.0)
        """
        super().__init__(
            dimension=DataQualityDimension.ACCURACY, threshold=threshold, weight=weight
        )
        self.field_validators = field_validators

    def check(self, data: List[Dict[str, Any]]) -> DataQualityResult:
        """
        Check data accuracy.

        Args:
            data: List of records to check

        Returns:
            DataQualityResult with accuracy score
        """
        if not data:
            return DataQualityResult(
                dimension=self.dimension,
                score=0.0,
                passed=False,
                threshold=self.threshold,
                details={"error": "Empty dataset"},
            )

        total_checks = 0
        valid_values = 0
        errors_by_field = {field: 0 for field in self.field_validators}

        for record in data:
            for field, validator in self.field_validators.items():
                total_checks += 1
                value = record.get(field)

                try:
                    if validator(value):
                        valid_values += 1
                    else:
                        errors_by_field[field] += 1
                except Exception:
                    errors_by_field[field] += 1

        score = valid_values / total_checks if total_checks > 0 else 0.0

        return DataQualityResult(
            dimension=self.dimension,
            score=score,
            passed=score >= self.threshold,
            threshold=self.threshold,
            details={
                "total_checks": total_checks,
                "valid_values": valid_values,
                "invalid_values": total_checks - valid_values,
                "errors_by_field": errors_by_field,
                "accuracy_percentage": f"{score:.2%}",
            },
        )


class ConsistencyCheck(DataQualityCheck):
    """
    Consistency: Checks if data follows business rules and relationships.

    Validates that records satisfy business logic and cross-field constraints.

    Example:
        >>> rules = [
        ...     lambda r: r.get('state') is not None if r.get('city') else True,
        ...     lambda r: r.get('website_url') or r.get('phone')  # At least one contact
        ... ]
        >>> check = ConsistencyCheck(rules)
        >>> result = check.check(data)
    """

    def __init__(
        self,
        business_rules: List[Callable[[Dict[str, Any]], bool]],
        rule_names: Optional[List[str]] = None,
        threshold: float = 0.95,
        weight: float = 1.0,
    ):
        """
        Initialize consistency check.

        Args:
            business_rules: List of functions that validate records
            rule_names: Optional names for each rule (for reporting)
            threshold: Minimum acceptable consistency (default: 0.95)
            weight: Importance weight (default: 1.0)
        """
        super().__init__(
            dimension=DataQualityDimension.CONSISTENCY,
            threshold=threshold,
            weight=weight,
        )
        self.business_rules = business_rules
        self.rule_names = rule_names or [
            f"Rule_{i+1}" for i in range(len(business_rules))
        ]

    def check(self, data: List[Dict[str, Any]]) -> DataQualityResult:
        """
        Check data consistency.

        Args:
            data: List of records to check

        Returns:
            DataQualityResult with consistency score
        """
        if not data:
            return DataQualityResult(
                dimension=self.dimension,
                score=0.0,
                passed=False,
                threshold=self.threshold,
                details={"error": "Empty dataset"},
            )

        total_checks = len(data) * len(self.business_rules)
        consistent_records = 0
        violations_by_rule = {name: 0 for name in self.rule_names}

        for record in data:
            for rule, rule_name in zip(self.business_rules, self.rule_names):
                try:
                    if rule(record):
                        consistent_records += 1
                    else:
                        violations_by_rule[rule_name] += 1
                except Exception:
                    violations_by_rule[rule_name] += 1

        score = consistent_records / total_checks if total_checks > 0 else 0.0

        return DataQualityResult(
            dimension=self.dimension,
            score=score,
            passed=score >= self.threshold,
            threshold=self.threshold,
            details={
                "total_checks": total_checks,
                "consistent_records": consistent_records,
                "violations": total_checks - consistent_records,
                "violations_by_rule": violations_by_rule,
                "consistency_percentage": f"{score:.2%}",
            },
        )


class TimelinessCheck(DataQualityCheck):
    """
    Timeliness: Checks if data is fresh and up-to-date.

    Validates that data was updated recently within acceptable time window.

    Example:
        >>> check = TimelinessCheck(
        ...     timestamp_field='updated_at',
        ...     max_age_hours=24
        ... )
        >>> result = check.check(data)
    """

    def __init__(
        self,
        timestamp_field: str,
        max_age_hours: int = 24,
        threshold: float = 0.95,
        weight: float = 1.0,
    ):
        """
        Initialize timeliness check.

        Args:
            timestamp_field: Name of field containing timestamp
            max_age_hours: Maximum acceptable age in hours (default: 24)
            threshold: Minimum acceptable freshness (default: 0.95)
            weight: Importance weight (default: 1.0)
        """
        super().__init__(
            dimension=DataQualityDimension.TIMELINESS,
            threshold=threshold,
            weight=weight,
        )
        self.timestamp_field = timestamp_field
        self.max_age = timedelta(hours=max_age_hours)

    def check(self, data: List[Dict[str, Any]]) -> DataQualityResult:
        """
        Check data timeliness.

        Args:
            data: List of records to check

        Returns:
            DataQualityResult with timeliness score
        """
        if not data:
            return DataQualityResult(
                dimension=self.dimension,
                score=0.0,
                passed=False,
                threshold=self.threshold,
                details={"error": "Empty dataset"},
            )

        now = datetime.now()
        fresh_records = 0
        stale_records = 0
        missing_timestamp = 0

        for record in data:
            timestamp_value = record.get(self.timestamp_field)

            if not timestamp_value:
                missing_timestamp += 1
                continue

            try:
                # Parse timestamp (support various formats)
                if isinstance(timestamp_value, str):
                    timestamp = datetime.fromisoformat(
                        timestamp_value.replace("Z", "+00:00")
                    )
                elif isinstance(timestamp_value, datetime):
                    timestamp = timestamp_value
                else:
                    missing_timestamp += 1
                    continue

                age = now - timestamp
                if age <= self.max_age:
                    fresh_records += 1
                else:
                    stale_records += 1

            except Exception:
                missing_timestamp += 1

        total_valid = fresh_records + stale_records
        score = fresh_records / total_valid if total_valid > 0 else 0.0

        return DataQualityResult(
            dimension=self.dimension,
            score=score,
            passed=score >= self.threshold,
            threshold=self.threshold,
            details={
                "fresh_records": fresh_records,
                "stale_records": stale_records,
                "missing_timestamp": missing_timestamp,
                "max_age_hours": self.max_age.total_seconds() / 3600,
                "timeliness_percentage": f"{score:.2%}",
            },
        )


class ValidityCheck(DataQualityCheck):
    """
    Validity: Checks if data conforms to expected schema and types.

    Validates that all fields have correct data types and structure.

    Example:
        >>> schema = {
        ...     'id': str,
        ...     'name': str,
        ...     'latitude': (float, type(None)),
        ...     'longitude': (float, type(None))
        ... }
        >>> check = ValidityCheck(schema)
        >>> result = check.check(data)
    """

    def __init__(
        self, schema: Dict[str, Any], threshold: float = 0.95, weight: float = 1.0
    ):
        """
        Initialize validity check.

        Args:
            schema: Dict mapping field names to expected types
            threshold: Minimum acceptable validity (default: 0.95)
            weight: Importance weight (default: 1.0)
        """
        super().__init__(
            dimension=DataQualityDimension.VALIDITY, threshold=threshold, weight=weight
        )
        self.schema = schema

    def check(self, data: List[Dict[str, Any]]) -> DataQualityResult:
        """
        Check data validity.

        Args:
            data: List of records to check

        Returns:
            DataQualityResult with validity score
        """
        if not data:
            return DataQualityResult(
                dimension=self.dimension,
                score=0.0,
                passed=False,
                threshold=self.threshold,
                details={"error": "Empty dataset"},
            )

        total_checks = len(data) * len(self.schema)
        valid_fields = 0
        type_errors_by_field = {field: 0 for field in self.schema}

        for record in data:
            for field, expected_type in self.schema.items():
                value = record.get(field)

                # Handle None values
                if value is None:
                    if type(None) in (
                        expected_type
                        if isinstance(expected_type, tuple)
                        else (expected_type,)
                    ):
                        valid_fields += 1
                    else:
                        type_errors_by_field[field] += 1
                    continue

                # Check type
                expected_types = (
                    expected_type
                    if isinstance(expected_type, tuple)
                    else (expected_type,)
                )
                if isinstance(value, expected_types):
                    valid_fields += 1
                else:
                    type_errors_by_field[field] += 1

        score = valid_fields / total_checks if total_checks > 0 else 0.0

        return DataQualityResult(
            dimension=self.dimension,
            score=score,
            passed=score >= self.threshold,
            threshold=self.threshold,
            details={
                "total_checks": total_checks,
                "valid_fields": valid_fields,
                "type_errors": total_checks - valid_fields,
                "type_errors_by_field": type_errors_by_field,
                "validity_percentage": f"{score:.2%}",
            },
        )


class UniquenessCheck(DataQualityCheck):
    """
    Uniqueness: Checks for duplicate records based on key fields.

    Validates that there are no duplicate records based on specified key fields.

    Example:
        >>> check = UniquenessCheck('id')  # Single key
        >>> result = check.check(data)

        >>> check = UniquenessCheck(['id', 'name'])  # Composite key
        >>> result = check.check(data)
    """

    def __init__(
        self,
        key_fields: List[str] | str,
        threshold: float = 1.0,  # Stricter default: no duplicates allowed
        weight: float = 1.0,
    ):
        """
        Initialize uniqueness check.

        Args:
            key_fields: Field name or list of field names that form unique key
            threshold: Minimum acceptable uniqueness (default: 1.0)
            weight: Importance weight (default: 1.0)
        """
        super().__init__(
            dimension=DataQualityDimension.UNIQUENESS,
            threshold=threshold,
            weight=weight,
        )
        self.key_fields = [key_fields] if isinstance(key_fields, str) else key_fields

    def check(self, data: List[Dict[str, Any]]) -> DataQualityResult:
        """
        Check data uniqueness.

        Args:
            data: List of records to check

        Returns:
            DataQualityResult with uniqueness score
        """
        if not data:
            return DataQualityResult(
                dimension=self.dimension,
                score=1.0,  # Empty dataset has no duplicates
                passed=True,
                threshold=self.threshold,
                details={"total_records": 0},
            )

        seen_keys: Set[tuple] = set()
        duplicates = 0
        duplicate_keys = []

        for record in data:
            # Build composite key
            key_values = tuple(record.get(field) for field in self.key_fields)

            # Skip records with missing key fields
            if None in key_values:
                continue

            if key_values in seen_keys:
                duplicates += 1
                if len(duplicate_keys) < 10:  # Limit examples
                    duplicate_keys.append(dict(zip(self.key_fields, key_values)))
            else:
                seen_keys.add(key_values)

        total_records = len(data)
        unique_records = total_records - duplicates
        score = unique_records / total_records if total_records > 0 else 1.0

        return DataQualityResult(
            dimension=self.dimension,
            score=score,
            passed=score >= self.threshold,
            threshold=self.threshold,
            details={
                "total_records": total_records,
                "unique_records": unique_records,
                "duplicate_records": duplicates,
                "duplicate_examples": duplicate_keys[:5],  # Show first 5
                "uniqueness_percentage": f"{score:.2%}",
            },
        )
