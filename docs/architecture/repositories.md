# Repository Pattern - Data Access Layer

**Repository Pattern** abstrai o acesso a dados, fornecendo uma interface **collection-like** para entidades do domínio.

---

## 🎯 Quick Start

### Basic Usage

```python
from repositories import InMemoryBreweryRepository
from domain import Brewery

# Create repository
repo = InMemoryBreweryRepository()

# Add brewery
brewery = Brewery(id="1", name="Test Brewery", ...)
repo.add(brewery)

# Get brewery
found = repo.get_by_id("1")
print(found.name)  # "Test Brewery"

# Find by criteria
results = repo.find_by(brewery_type="micro")
print(f"Found {len(results)} micro breweries")

# Get all
all_breweries = repo.get_all()
```

### With Unit of Work (Transaction Management)

```python
from repositories import UnitOfWork

# Atomic transaction
with UnitOfWork() as uow:
    brewery = Brewery(id="1", ...)
    uow.breweries.add(brewery)
    
    # More operations...
    
    uow.commit()  # ← All or nothing!
```

---

## 📦 Components

### 1. IRepository[T] - Generic Interface

```python
from repositories import IRepository

class IRepository(ABC, Generic[T]):
    def get_by_id(id: str) -> Optional[T]
    def get_all() -> List[T]
    def add(entity: T) -> None
    def add_many(entities: List[T]) -> int
    def update(entity: T) -> None
    def remove(id: str) -> bool
    def exists(id: str) -> bool
    def count() -> int
```

**Benefits:**
- ✅ Type-safe with generics
- ✅ Standard interface across all repos
- ✅ Easy to mock for tests

---

### 2. IBreweryRepository - Domain-Specific

```python
class IBreweryRepository(IRepository[Brewery]):
    """Extended interface for Brewery-specific queries."""
    
    def find_by(self, **criteria) -> List[Brewery]:
        """Find breweries by flexible criteria."""
    
    def find_by_type(self, brewery_type: str) -> List[Brewery]:
        """Find breweries by type (micro, nano, etc)."""
    
    def find_by_location(self, city: str, state: str) -> List[Brewery]:
        """Find breweries by location."""
```

**Benefits:**
- ✅ Domain-specific queries
- ✅ Type-safe return values
- ✅ Clear contracts

---

### 3. Implementations

#### InMemoryBreweryRepository (Testing)

```python
from repositories import InMemoryBreweryRepository

repo = InMemoryBreweryRepository()

# Fast, in-memory storage
# Perfect for unit tests
# No database setup required
```

**Use for:**
- ✅ Unit tests
- ✅ Development/prototyping
- ✅ Integration test fixtures

---

#### SQLBreweryRepository (Production)

```python
from repositories import SQLBreweryRepository
from config import AzureSQLConfig

repo = SQLBreweryRepository(AzureSQLConfig())

# Persistent storage in Azure SQL
# Connection pooling
# Transaction support
```

**Use for:**
- ✅ Production
- ✅ Integration tests (with test DB)
- ✅ Data persistence

---

### 4. Unit of Work Pattern

**Purpose**: Manage transactions across multiple repositories.

```python
from repositories import IUnitOfWork, UnitOfWork

# Context manager - auto rollback on error
with UnitOfWork() as uow:
    # Access repositories
    brewery1 = Brewery(...)
    brewery2 = Brewery(...)
    
    # Add to transaction
    uow.breweries.add(brewery1)
    uow.breweries.add(brewery2)
    
    # Commit atomically
    uow.commit()
    # If any error → automatic rollback!
```

**Benefits:**
- ✅ Atomic transactions (all or nothing)
- ✅ Automatic rollback on errors
- ✅ Context manager support
- ✅ Consistent across repositories

---

## 🏗️ Architecture

```
repositories/
├── __init__.py              # Exports
├── base.py                  # IRepository[T], IBreweryRepository
├── brewery_repository.py    # InMemory, SQL implementations
└── unit_of_work.py          # IUnitOfWork, UnitOfWork, SQLUnitOfWork
```

---

## 📐 Design Patterns

### Repository Pattern

```python
# ❌ WITHOUT Repository
def get_brewery(id):
    conn = pyodbc.connect(CONNECTION_STRING)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Breweries WHERE id = ?", id)
    row = cursor.fetchone()
    # Manual mapping...
    return Brewery(...)

# ✅ WITH Repository
brewery = repository.get_by_id(id)
```

**Benefits:**
- ✅ Clean separation of concerns
- ✅ Easy to swap implementations
- ✅ Testable with mocks/in-memory
- ✅ No SQL in business logic

---

### Dependency Inversion

```python
# Use Cases depend on INTERFACE, not concrete implementation

class LoadBreweriesUseCase:
    def __init__(self, repository: IBreweryRepository):  # ← Interface!
        self.repository = repository
    
    def execute(self, breweries: List[Brewery]):
        # Works with ANY implementation
        self.repository.add_many(breweries)

# Production: Use SQL
use_case = LoadBreweriesUseCase(SQLBreweryRepository(config))

# Testing: Use InMemory
use_case = LoadBreweriesUseCase(InMemoryBreweryRepository())
```

---

## 💡 Tips

!!! tip "Testing"
    Always use `InMemoryBreweryRepository` for unit tests:
    ```python
    def test_load_breweries():
        repo = InMemoryBreweryRepository()  # ← Fast!
        use_case = LoadBreweriesUseCase(repo)
        
        breweries = [Brewery(...)]
        use_case.execute(breweries)
        
        assert repo.count() == 1
    ```

!!! warning "N+1 Queries"
    For production, batch operations when possible:
    ```python
    # ❌ N+1 queries
    for brewery in breweries:
        repo.add(brewery)
    
    # ✅ Single batch
    repo.add_many(breweries)  # Much faster!
    ```

!!! success "Unit of Work"
    Use for complex operations:
    ```python
    with UnitOfWork() as uow:
        # Multiple operations
        breweries = uow.breweries.find_by_type("micro")
        for brewery in breweries:
            # Update logic
            uow.breweries.update(brewery)
        
        # Atomic commit
        uow.commit()
    ```

---

## 🔧 Custom Repositories

```python
from repositories import IRepository
from typing import Generic, TypeVar

T = TypeVar('T')

class MyCustomRepository(IRepository[T]):
    def __init__(self, config):
        self._storage = {}
        self.config = config
    
    def get_by_id(self, id: str) -> Optional[T]:
        return self._storage.get(id)
    
    def add(self, entity: T) -> None:
        self._storage[entity.id] = entity
    
    # Implement other methods...
    
    # Custom methods
    def my_custom_query(self) -> List[T]:
        # Your custom logic
        pass
```

---

## 📖 References

- **Code**: `dags/repositories/`
- **API Reference**: Use `help(IBreweryRepository)` in Python
- **Domain Layer**: See [Domain Layer](domain-layer.md)
- **Use Cases**: See [Use Cases Layer](use-cases.md)

---

## 🎯 Comparison

| Feature | Direct DB Access | Repository Pattern |
|---------|------------------|-------------------|
| **Coupling** | High (SQL everywhere) | Low (abstracted) |
| **Testability** | Hard (needs DB) | Easy (in-memory) |
| **Flexibility** | Low (hard to swap DB) | High (interface-based) |
| **Maintenance** | Hard (scattered SQL) | Easy (centralized) |
| **Type Safety** | None | Full (generics) |

