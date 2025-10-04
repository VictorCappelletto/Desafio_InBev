# Data Quality Framework

Framework robusto de qualidade de dados baseado em **6 dimensões ISO 8000**.

---

## 🎯 Quick Start

```python
from data_quality.rules import create_brewery_quality_engine

# Create pre-configured engine
engine = create_brewery_quality_engine(strict_mode=False)

# Run checks
brewery_data = [{"id": "1", "name": "Brewery A", ...}]
report = engine.run_checks(brewery_data)

# Check results
if report.is_overall_passed():
    print("✅ Data quality passed!")
else:
    print(f"❌ Issues: {report.summary()}")
```

---

## 📊 6 Quality Dimensions

| Dimension | Check | Purpose |
|-----------|-------|---------|
| **Completeness** | Required fields present | `name`, `brewery_type`, `city` not null |
| **Accuracy** | Valid coordinates | Lat: -90 to 90, Lon: -180 to 180 |
| **Consistency** | State/country match | US states = "United States" |
| **Timeliness** | Recent updates | Data < 1 year old |
| **Validity** | Enum values | `brewery_type` in allowed list |
| **Uniqueness** | No duplicates | Unique `id` field |

---

## 🏗️ Architecture

```python
# Core Components
DataQualityCheck        # Abstract base class
DataQualityEngine       # Orchestrates checks
DataQualityReport       # Results aggregation

# Concrete Checks (dags/data_quality/dimensions.py)
CompletenessCheck, AccuracyCheck, ConsistencyCheck
TimelinessCheck, ValidityCheck, UniquenessCheck
SchemaCheck, FreshnessCheck
```

---

## 🔧 Custom Checks

```python
from data_quality.framework import DataQualityCheck, DataQualityCheckResult

class CustomCheck(DataQualityCheck):
    def __init__(self, threshold=0.95):
        super().__init__("CustomCheck", "Custom", threshold)
    
    def run(self, data, **kwargs):
        # Your validation logic
        score = calculate_score(data)
        
        return DataQualityCheckResult(
            check_name=self.name,
            dimension=self.dimension,
            status="PASSED" if score >= self.threshold else "FAILED",
            score=score,
            message=f"Score: {score:.2f}"
        )

# Use it
engine = DataQualityEngine()
engine.add_check(CustomCheck(threshold=0.90))
```

---

## 📖 References

- **Code**: `dags/data_quality/`
- **API Reference**: Use `help(DataQualityEngine)` in Python
- **Brewery Rules**: `dags/data_quality/rules/brewery_rules.py`

---

## 💡 Tips

!!! tip "Strict Mode"
    Use `strict_mode=True` to fail fast on first error:
    ```python
    engine = create_brewery_quality_engine(strict_mode=True)
    ```

!!! warning "Performance"
    For large datasets (>100k records), run checks in batches:
    ```python
    for batch in chunked(data, size=10000):
        report = engine.run_checks(batch)
    ```

!!! success "Integration"
    Use in Airflow DAGs via `ValidateBreweriesQualityUseCase`:
    ```python
    from use_cases import ValidateBreweriesQualityUseCase
    
    use_case = ValidateBreweriesQualityUseCase(engine)
    report = use_case.execute(breweries)
    ```

