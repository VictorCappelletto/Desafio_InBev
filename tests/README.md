# Tests

**Comprehensive test suite for the Desafio InBev project.**

---

## Overview

The project follows a comprehensive testing strategy with **unit tests** to ensure code quality and system reliability.

---

## Test Structure

```
tests/
├── __init__.py
├── conftest.py                    # Shared fixtures and pytest config
├── README.md                      # This file
├── test_config.py                 # Unit: Configuration classes
└── test_services.py               # Unit: ETL services
```

---

## Test Types

### **1. Unit Tests**
Test individual components in isolation.

**Files:**
- `test_config.py` - Configuration dataclasses
- `test_services.py` - ETL services (extractor, transformer, loader)

**Run:**
```bash
pytest tests/ -v
```

---

## Running Tests

### **All Tests**
```bash
# Using poetry (recommended)
poetry run pytest -v

# Or using taskipy
poetry run task test
```

### **With Coverage**
```bash
# Generate HTML coverage report
poetry run pytest --cov=dags --cov-report=html --cov-report=term -v

# Or using taskipy
poetry run task test-cov
```

**Coverage report:** `htmlcov/index.html`

---

### **Specific Test Suites**

```bash
# All tests
pytest tests/ -v

# Specific file
pytest tests/test_config.py -v

# Specific test class
pytest tests/test_config.py::TestConfigClasses -v

# Specific test method
pytest tests/test_config.py::TestConfigClasses::test_config_loading -v
```

---

### **Using Markers**

```bash
# Run only unit tests
pytest -m unit -v

# Skip slow tests
pytest -m "not slow" -v
```

---

## Test Coverage

**Target:** >60% overall coverage (unit tests)

### **Current Coverage by Layer**

| Layer | Coverage | Status |
|-------|----------|--------|
| **Config** | ~90% | Excellent |
| **Services** | ~85% | Excellent |
| **Overall** | **~60%** | **Good** |

---

## Test Markers

Available pytest markers:

| Marker | Description | Usage |
|--------|-------------|-------|
| `@pytest.mark.unit` | Unit test | `pytest -m unit` |
| `@pytest.mark.slow` | Slow test (>1s) | `pytest -m slow` |

---

## Available Fixtures

### **Configuration Fixtures** (conftest.py)
- `mock_api_config` - Mocked API configuration
- `mock_sql_config` - Mocked Azure SQL configuration
- `mock_databricks_config` - Mocked Databricks configuration

### **Data Fixtures** (conftest.py)
- `sample_brewery_data` - Raw API response data
- `sample_invalid_brewery_data` - Invalid data for validation tests
- `sample_brewery_entity` - Domain entity (Brewery)
- `sample_raw_brewery_dict` - Single brewery dictionary

### **Repository Fixtures** (conftest.py)
- `in_memory_repository` - Fresh InMemoryBreweryRepository

---

## Best Practices

### **1. Arrange-Act-Assert Pattern**
```python
def test_something():
    # Arrange - setup test data
    repository = InMemoryBreweryRepository()
    brewery = Brewery(id="1", name="Test", brewery_type=BreweryType.MICRO)
    
    # Act - execute the operation
    repository.add(brewery)
    
    # Assert - verify the result
    assert repository.count() == 1
```

### **2. Use Descriptive Test Names**
```python
# GOOD
def test_extract_retries_on_transient_failures():
    pass

# BAD
def test_extract():
    pass
```

### **3. Test One Thing**
```python
# GOOD - focused test
def test_add_brewery_increases_count():
    repository.add(brewery)
    assert repository.count() == 1

# BAD - tests multiple things
def test_repository():
    repository.add(brewery)
    assert repository.count() == 1
    repository.update(brewery)
    repository.remove(brewery.id)
```

### **4. Use Fixtures for Setup**
```python
# GOOD - uses fixture
def test_add(in_memory_repository, sample_brewery_entity):
    in_memory_repository.add(sample_brewery_entity)
    assert in_memory_repository.count() == 1

# BAD - manual setup in every test
def test_add():
    repository = InMemoryBreweryRepository()
    brewery = Brewery(...)
    repository.add(brewery)
```

---

## Debugging Tests

### **Verbose Output**
```bash
pytest -v -s
```

### **Stop on First Failure**
```bash
pytest -x
```

### **Run Failed Tests Only**
```bash
pytest --lf
```

### **Show Full Diff**
```bash
pytest -vv
```

### **Show Print Statements**
```bash
pytest -s
```

### **Debug with pdb**
```python
def test_something():
    import pdb; pdb.set_trace()
    # Your test code
```

---

## CI/CD Integration

Tests run automatically in GitHub Actions:

```yaml
# .github/workflows/ci.yml
- name: Run Tests
  run: |
    poetry run pytest \
      --cov=dags \
      --cov-report=xml \
      --cov-report=term \
      -v
```

**CI workflow:**
1. Lint code (black, isort)
2. Run unit tests
3. Generate coverage report
4. Build Docker image
5. Security scans
6. Deploy documentation

---

## Writing New Tests

### **Unit Test Example**

```python
# tests/test_my_feature.py
import pytest
from my_module import MyClass

@pytest.mark.unit
class TestMyClass:
    """Test MyClass functionality."""
    
    def test_something(self):
        """Test specific behavior."""
        # Arrange
        obj = MyClass()
        
        # Act
        result = obj.do_something()
        
        # Assert
        assert result == expected_value
```

---

## Test Coverage Goals

### **Current Status: 60% overall (Unit Tests)**

### **Breakdown:**
- **Config:** 90% (Excellent)
- **Services:** 85% (Excellent)
- **Overall:** 60% (Good for unit tests)

### **Next Steps:**
1. Add more edge case tests
2. Improve observability coverage
3. Add data quality tests

---

## Related Documentation

- [Pytest Documentation →](https://docs.pytest.org/)
- [Coverage.py Documentation →](https://coverage.readthedocs.io/)
- [Project README →](../README.md)
- [CI/CD Workflows →](../.github/workflows/)

---

## Pre-Commit Checklist

Before committing code:

- [ ] All tests pass (`pytest -v`)
- [ ] Coverage > 60% (`pytest --cov`)
- [ ] New features have unit tests
- [ ] Test names are descriptive
- [ ] Tests are independent
- [ ] Fixtures are reused
- [ ] No commented-out tests

---

## Quick Commands

```bash
# Run all tests
poetry run task test

# Run with coverage
poetry run task test-cov

# Run fast tests only
pytest -m "not slow" -v

# Run and open coverage report
poetry run task test-cov && open htmlcov/index.html
```

---

**Goal:** Maintain >60% unit test coverage and 100% passing tests!

