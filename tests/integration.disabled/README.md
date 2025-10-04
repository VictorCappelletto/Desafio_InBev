# Integration Tests

**Comprehensive integration tests covering the complete system.**

---

## 📋 Overview

Integration tests verify that multiple components work together correctly. Unlike unit tests (which test components in isolation), integration tests ensure proper interaction between layers.

---

## 🗂️ Test Structure

```
tests/integration/
├── __init__.py
├── test_full_pipeline.py      # E2E pipeline tests
├── test_repositories.py        # Repository + Unit of Work tests
├── test_use_cases.py          # Use Cases layer tests
├── test_domain_layer.py       # Domain entities + validation tests
└── README.md                  # This file
```

---

## 🧪 Test Suites

### **1. test_full_pipeline.py** (E2E)
**Purpose:** End-to-end pipeline testing

**Tests:**
- ✅ Complete ETL pipeline (Extract → Transform → Load → Validate)
- ✅ Extraction failures handling
- ✅ Invalid data handling
- ✅ Quality filtering
- ✅ Duplicate handling
- ✅ Real API extractor (mocked requests)
- ✅ Metrics collection

**Run:**
```bash
pytest tests/integration/test_full_pipeline.py -v
```

---

### **2. test_repositories.py**
**Purpose:** Repository Pattern + Unit of Work

**Tests:**
- ✅ CRUD operations (Create, Read, Update, Delete)
- ✅ Batch operations (add_many)
- ✅ Query operations (find_by_type, find_by_location)
- ✅ Duplicate detection
- ✅ Unit of Work commit
- ✅ Unit of Work rollback on error
- ✅ Context manager support

**Run:**
```bash
pytest tests/integration/test_repositories.py -v
```

---

### **3. test_use_cases.py**
**Purpose:** Application Logic (Use Cases Layer)

**Tests:**
- ✅ ExtractBreweriesUseCase (with retry logic)
- ✅ TransformBreweriesUseCase (validation + skipping)
- ✅ LoadBreweriesUseCase (quality filtering)
- ✅ ValidateBreweriesQualityUseCase (strict mode)
- ✅ Error handling
- ✅ Empty input handling
- ✅ Metrics collection

**Run:**
```bash
pytest tests/integration/test_use_cases.py -v
```

---

### **4. test_domain_layer.py**
**Purpose:** Domain-Driven Design (DDD)

**Tests:**
- ✅ Value Objects (Coordinates, Address, Location, Contact)
- ✅ Immutability enforcement
- ✅ Validation (coordinates, names, types)
- ✅ Brewery entity creation
- ✅ Factory methods (from_dict)
- ✅ Aggregate quality scoring
- ✅ Domain validators

**Run:**
```bash
pytest tests/integration/test_domain_layer.py -v
```

---

## 🚀 Running Tests

### **All Integration Tests**
```bash
pytest tests/integration/ -v
```

### **With Coverage**
```bash
pytest tests/integration/ --cov=dags --cov-report=html --cov-report=term
```

### **Specific Test Class**
```bash
pytest tests/integration/test_full_pipeline.py::TestFullETLPipeline -v
```

### **Specific Test Method**
```bash
pytest tests/integration/test_full_pipeline.py::TestFullETLPipeline::test_full_pipeline_success -v
```

### **With Markers**
```bash
# Run only integration tests
pytest -m integration -v

# Run E2E tests
pytest -m e2e -v

# Skip slow tests
pytest -m "not slow" -v
```

---

## 📊 Test Coverage

**Target:** >80% coverage

**Current Layers:**
- ✅ **E2E Pipeline:** Complete flow coverage
- ✅ **Repositories:** CRUD + UoW coverage
- ✅ **Use Cases:** All 4 use cases covered
- ✅ **Domain:** Entities + VOs + Validators covered

---

## 🎯 Test Markers

Tests can be marked with pytest markers:

```python
@pytest.mark.integration
def test_something():
    """Integration test."""
    pass

@pytest.mark.e2e
def test_full_flow():
    """End-to-end test."""
    pass

@pytest.mark.slow
def test_expensive():
    """Slow test (>1s)."""
    pass
```

**Run tests by marker:**
```bash
pytest -m integration  # Only integration tests
pytest -m e2e          # Only E2E tests
pytest -m "not slow"   # Skip slow tests
```

---

## 🔧 Fixtures Available

### **From conftest.py:**
- `sample_brewery_data` - Raw API data
- `sample_brewery_entity` - Domain entity
- `sample_raw_brewery_dict` - Single brewery dict
- `in_memory_repository` - Fresh repository
- `mock_api_config` - Mocked API config
- `mock_sql_config` - Mocked SQL config
- `mock_databricks_config` - Mocked Databricks config

### **Usage:**
```python
def test_something(sample_brewery_entity, in_memory_repository):
    """Test using fixtures."""
    in_memory_repository.add(sample_brewery_entity)
    assert in_memory_repository.count() == 1
```

---

## 💡 Best Practices

### **1. Test Independence**
Each test should be independent and not rely on other tests:

```python
# ✅ Good - uses fixture for fresh state
def test_add(in_memory_repository):
    in_memory_repository.add(brewery)
    assert in_memory_repository.count() == 1

# ❌ Bad - relies on previous test
def test_get():
    brewery = repository.get_by_id("1")  # Where did this come from?
```

### **2. Clear Test Names**
```python
# ✅ Good - describes what is tested
def test_pipeline_with_duplicate_handling():
    pass

# ❌ Bad - vague
def test_pipeline():
    pass
```

### **3. Arrange-Act-Assert Pattern**
```python
def test_something():
    # Arrange - setup
    repository = InMemoryBreweryRepository()
    brewery = Brewery(...)
    
    # Act - execute
    repository.add(brewery)
    
    # Assert - verify
    assert repository.count() == 1
```

### **4. Test One Thing**
```python
# ✅ Good - tests one behavior
def test_add_brewery():
    repository.add(brewery)
    assert repository.count() == 1

# ❌ Bad - tests multiple behaviors
def test_repository():
    repository.add(brewery)
    assert repository.count() == 1
    repository.update(brewery)
    assert brewery.name == "Updated"
    repository.remove(brewery.id)
    assert repository.count() == 0
```

---

## 🐛 Debugging Tests

### **Run with verbose output:**
```bash
pytest tests/integration/ -v -s
```

### **Stop on first failure:**
```bash
pytest tests/integration/ -x
```

### **Run failed tests only:**
```bash
pytest tests/integration/ --lf
```

### **Show print statements:**
```bash
pytest tests/integration/ -s
```

### **Show full diff:**
```bash
pytest tests/integration/ -vv
```

---

## 📈 CI/CD Integration

Tests run automatically in CI/CD:

```yaml
# .github/workflows/ci.yml
- name: Run Integration Tests
  run: |
    pytest tests/integration/ \
      --cov=dags \
      --cov-report=xml \
      --cov-report=term \
      -v
```

---

## 🔗 Related

- [Unit Tests →](../test_config.py)
- [Conftest →](../conftest.py)
- [Domain Layer →](../../dags/domain/README.md)
- [Use Cases →](../../dags/use_cases/__init__.py)
- [Repositories →](../../dags/repositories/README.md)

---

## ✅ Checklist

Before committing:
- [ ] All integration tests pass
- [ ] Coverage > 80%
- [ ] No skipped tests (unless documented)
- [ ] Test names are descriptive
- [ ] Fixtures are used appropriately
- [ ] Tests are independent
- [ ] One assertion per test (preferably)

---

**Run all tests:**
```bash
poetry run task test
```

**With coverage:**
```bash
poetry run task test-cov
```

