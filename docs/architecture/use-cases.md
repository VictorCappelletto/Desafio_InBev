# Use Cases Layer - Application Logic

**Use Cases Layer** contém a **lógica de aplicação** que orquestra o fluxo de dados entre interfaces externas e o domínio.

---

## Quick Start

```python
from use_cases import (
 ExtractBreweriesUseCase,
 TransformBreweriesUseCase,
 LoadBreweriesUseCase,
 ValidateBreweriesQualityUseCase
)
from services import BreweryAPIExtractor
from repositories import InMemoryBreweryRepository
from data_quality.rules import create_brewery_quality_engine

# 1. Extract
extract_uc = ExtractBreweriesUseCase(BreweryAPIExtractor(config))
raw_data = extract_uc.execute()

# 2. Transform
transform_uc = TransformBreweriesUseCase()
breweries = transform_uc.execute(raw_data)

# 3. Validate Quality
quality_uc = ValidateBreweriesQualityUseCase(create_brewery_quality_engine())
report = quality_uc.execute(breweries)

# 4. Load
if report.is_overall_passed():
 load_uc = LoadBreweriesUseCase(InMemoryBreweryRepository())
 count = load_uc.execute(breweries)
 print(f" Loaded {count} breweries")
```

---

## Use Cases

### 1. ExtractBreweriesUseCase

**Purpose**: Extract raw data from external source.

```python
class ExtractBreweriesUseCase:
 def __init__(self, extractor: IDataExtractor):
 self.extractor = extractor

 def execute(self, **extraction_params) -> List[Dict[str, Any]]:
 """
 Extract brewery data with retry logic.

 Returns:
 List of raw brewery dictionaries

 Raises:
 ExtractionError: If extraction fails after retries
 """
```

**Features:**
- Automatic retry (3 attempts)
- Exponential backoff
- Structured logging
- Error handling

**Usage in DAG:**
```python
@task
def extract_data(**context):
 use_case = ExtractBreweriesUseCase(
 ETLFactory.create_brewery_extractor()
 )
 data = use_case.execute(per_page=50)
 return data
```

---

### 2. TransformBreweriesUseCase

**Purpose**: Transform raw data into domain entities.

```python
class TransformBreweriesUseCase:
 def execute(self, raw_data: List[Dict[str, Any]]) -> List[Brewery]:
 """
 Transform raw data to Brewery entities.

 Returns:
 List of validated Brewery entities

 Raises:
 TransformationError: If transformation fails
 """
```

**Features:**
- Converts dicts → `Brewery` entities
- Validates each entity
- Skips invalid data with logging
- Calculates transformation metrics

**Usage in DAG:**
```python
@task
def transform_data(raw_data: List[Dict], **context):
 use_case = TransformBreweriesUseCase()
 breweries = use_case.execute(raw_data)
 return breweries
```

---

### 3. LoadBreweriesUseCase

**Purpose**: Persist entities to repository.

```python
class LoadBreweriesUseCase:
 def __init__(self, repository: IBreweryRepository):
 self.repository = repository

 def execute(
 self, 
 breweries: List[Brewery],
 min_quality: float = 0.5
 ) -> int:
 """
 Load breweries with quality filtering.

 Args:
 breweries: List of Brewery entities
 min_quality: Minimum quality score (0.0-1.0)

 Returns:
 Number of breweries loaded
 """
```

**Features:**
- Quality-based filtering
- Batch loading for performance
- Duplicate detection
- Validation before persisting

**Usage in DAG:**
```python
@task
def load_data(breweries: List[Brewery], **context):
 use_case = LoadBreweriesUseCase(
 SQLBreweryRepository(AzureSQLConfig())
 )
 count = use_case.execute(breweries, min_quality=0.7)
 return count
```

---

### 4. ValidateBreweriesQualityUseCase

**Purpose**: Run data quality checks.

```python
class ValidateBreweriesQualityUseCase:
 def __init__(self, quality_engine: DataQualityEngine):
 self.quality_engine = quality_engine

 def execute(self, breweries: List[Brewery]) -> DataQualityReport:
 """
 Validate breweries against quality rules.

 Returns:
 DataQualityReport with results

 Raises:
 ValidationError: If strict_mode=True and checks fail
 """
```

**Features:**
- 6 quality dimensions (ISO 8000)
- Comprehensive reporting
- Strict mode for fail-fast
- Detailed failure reasons

**Usage in DAG:**
```python
@task
def validate_quality(breweries: List[Brewery], **context):
 engine = create_brewery_quality_engine(strict_mode=False)
 use_case = ValidateBreweriesQualityUseCase(engine)

 report = use_case.execute(breweries)

 if not report.is_overall_passed():
 send_alert(f"Quality issues: {report.summary()}")

 return report.to_dict()
```

---

## Architecture

```
use_cases/
 __init__.py # Exports
 extract.py # ExtractBreweriesUseCase
 transform.py # TransformBreweriesUseCase
 load.py # LoadBreweriesUseCase
 quality.py # ValidateBreweriesQualityUseCase
```

---

## Clean Architecture Rules

### Dependencies

```
Use Cases CAN depend on:
 Domain (entities, value objects, exceptions)
 Interfaces (IDataExtractor, IBreweryRepository)
 Data Quality (DataQualityEngine)

Use Cases CANNOT depend on:
 Infrastructure (Azure, Databricks, etc)
 Services (concrete implementations)
 DAGs (orchestration layer)
 External libraries (requests, pyodbc, etc)
```

### Single Responsibility

Each use case has **one reason to change**:

| Use Case | Responsibility | Changes When |
|----------|----------------|--------------|
| Extract | Get raw data | API changes |
| Transform | Create entities | Business rules change |
| Load | Persist data | Storage strategy changes |
| Validate | Check quality | Quality rules change |

---

## Tips

!!! tip "Dependency Injection"
 Always inject dependencies (never instantiate inside):
 ```python
 # Good - testable
 class LoadBreweriesUseCase:
 def __init__(self, repository: IBreweryRepository):
 self.repository = repository

 # Bad - hard to test
 class LoadBreweriesUseCase:
 def __init__(self):
 self.repository = SQLBreweryRepository() # Tight coupling!
 ```

!!! warning "Error Handling"
 Use domain exceptions, not infrastructure exceptions:
 ```python
 # Good
 try:
 data = self.extractor.extract()
 except Exception as e:
 raise ExtractionError(f"Failed to extract: {e}") from e

 # Bad - leaks infrastructure details
 data = requests.get(url) # Raises RequestException
 ```

!!! success "Composability"
 Use cases can call other use cases:
 ```python
 class FullETLUseCase:
 def execute(self):
 # Compose multiple use cases
 raw_data = self.extract_uc.execute()
 breweries = self.transform_uc.execute(raw_data)
 report = self.quality_uc.execute(breweries)

 if report.is_overall_passed():
 count = self.load_uc.execute(breweries)
 return count
 ```

---

## Custom Use Cases

```python
from use_cases import ExtractBreweriesUseCase
from domain import Brewery
from typing import List

class EnrichBreweriesUseCase:
 """Custom use case for data enrichment."""

 def __init__(self, geocoding_service):
 self.geocoding_service = geocoding_service

 def execute(self, breweries: List[Brewery]) -> List[Brewery]:
 """Enrich breweries with coordinates."""
 enriched = []

 for brewery in breweries:
 if not brewery.location or not brewery.location.coordinates:
 # Geocode address
 coords = self.geocoding_service.geocode(
 brewery.location.address
 )
 brewery.location.coordinates = coords

 enriched.append(brewery)

 return enriched

# Use in pipeline
@task
def enrich_data(breweries: List[Brewery]):
 use_case = EnrichBreweriesUseCase(GoogleMapsAPI())
 return use_case.execute(breweries)
```

---

## References

- **Code**: `dags/use_cases/`
- **API Reference**: Use `help(ExtractBreweriesUseCase)` in Python
- **Domain Layer**: See [Domain Layer](domain-layer.md)
- **Repositories**: See [Repository Pattern](repositories.md)
- **Data Quality**: See [Data Quality Framework](../guides/data-quality.md)

---

## Complete Pipeline Example

```python
# Complete ETL pipeline using all 4 use cases

def brewery_etl_pipeline():
 # 1⃣ Extract
 extractor = ETLFactory.create_brewery_extractor()
 extract_uc = ExtractBreweriesUseCase(extractor)
 raw_data = extract_uc.execute(per_page=100, by_state="california")

 # 2⃣ Transform
 transform_uc = TransformBreweriesUseCase()
 breweries = transform_uc.execute(raw_data)

 # 3⃣ Validate Quality
 engine = create_brewery_quality_engine(strict_mode=False)
 quality_uc = ValidateBreweriesQualityUseCase(engine)
 report = quality_uc.execute(breweries)

 if not report.is_overall_passed():
 logger.warning(f"Quality issues: {report.summary()}")
 # Filter low-quality data
 breweries = [b for b in breweries 
 if BreweryAggregate(b).calculate_quality_score() >= 0.7]

 # 4⃣ Load
 repository = SQLBreweryRepository(AzureSQLConfig())
 load_uc = LoadBreweriesUseCase(repository)
 count = load_uc.execute(breweries, min_quality=0.7)

 logger.info(f" ETL Complete: {count} breweries loaded")
 return count
```

