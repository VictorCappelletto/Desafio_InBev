# Domain Layer - Clean Architecture

**Domain Layer** contém as **regras de negócio** e **entidades do domínio**. É o núcleo da aplicação, independente de infraestrutura.

---

## Quick Start

```python
from domain import Brewery, BreweryAggregate, Coordinates, Address

# Create value objects
coords = Coordinates(latitude=37.7749, longitude=-122.4194)
address = Address(
 street="123 Main St",
 city="San Francisco",
 state="California",
 postal_code="94102"
)

# Create entity
brewery = Brewery(
 id="brewery-123",
 name="Golden Gate Brewing",
 brewery_type="micro",
 location=Location(coordinates=coords, address=address)
)

# Create aggregate (with validation)
aggregate = BreweryAggregate.from_dict({
 "id": "brewery-123",
 "name": "Golden Gate Brewing",
 # ... more fields
})

# Calculate quality
quality = aggregate.calculate_quality_score()
print(f"Quality: {quality:.2%}")
```

---

## Components

### 1. Value Objects (Immutable)

**Purpose**: Represent concepts with no identity, only value.

```python
# dags/domain/value_objects.py

@dataclass(frozen=True) # ← Immutable!
class Coordinates:
 latitude: float
 longitude: float

 def __post_init__(self):
 # Validation in constructor
 if not -90 <= self.latitude <= 90:
 raise InvalidCoordinatesError(...)

# Other value objects:
Address, Location, Contact, BreweryType
```

**Key Traits:**
- Immutable (`frozen=True`)
- Validated on creation
- No identity (equality by value)
- Self-contained business rules

---

### 2. Entities

**Purpose**: Objects with identity that can change over time.

```python
# dags/domain/entities.py

@dataclass
class Brewery:
 id: str # ← Identity!
 name: str
 brewery_type: BreweryType
 location: Optional[Location] = None
 contact: Optional[Contact] = None

 @classmethod
 def from_dict(cls, data: dict) -> "Brewery":
 # Factory method with validation
 ...
```

**Key Traits:**
- Has identity (`id`)
- Mutable (can change state)
- Equality by ID (not value)
- Factory methods for creation

---

### 3. Aggregates

**Purpose**: Cluster of entities treated as a single unit with an **Aggregate Root**.

```python
# dags/domain/entities.py

class BreweryAggregate:
 """Aggregate Root for Brewery domain."""

 def __init__(self, brewery: Brewery):
 self.brewery = brewery # ← Root entity
 self._events: List[DomainEvent] = []

 def calculate_quality_score(self) -> float:
 """Business logic encapsulated in aggregate."""
 score = 0.5 # Base score

 # Completeness scoring
 if self.brewery.location: score += 0.15
 if self.brewery.contact: score += 0.15

 # Data quality scoring
 if self.brewery.brewery_type: score += 0.10
 if self.brewery.location and self.brewery.location.address:
 if self.brewery.location.address.city: score += 0.05
 if self.brewery.location.address.state: score += 0.05

 return min(score, 1.0)
```

**Key Traits:**
- Enforces invariants (business rules)
- Transactional boundary
- Encapsulates complex logic
- Can emit domain events

---

### 4. Validators

**Purpose**: Separate business rule validation logic.

```python
# dags/domain/validators.py

class BreweryValidator:
 @staticmethod
 def validate_name(name: str) -> None:
 if not name or len(name.strip()) < 2:
 raise InvalidBreweryNameError(...)

 @staticmethod
 def validate_type(brewery_type: str) -> None:
 if brewery_type not in VALID_TYPES:
 raise InvalidBreweryTypeError(...)

# Usage in entity
def __post_init__(self):
 BreweryValidator.validate_name(self.name)
 BreweryValidator.validate_type(self.brewery_type)
```

---

### 5. Domain Exceptions

**Purpose**: Business-specific errors with rich context.

```python
# dags/domain/exceptions.py

class DomainException(Exception):
 """Base for all domain exceptions."""

class InvalidBreweryNameError(DomainException): pass
class InvalidCoordinatesError(DomainException): pass
class DuplicateBreweryError(DomainException): pass
# ... 4 more
```

---

## Architecture

```
domain/
 __init__.py # Exports
 value_objects.py # Coordinates, Address, Location, Contact, BreweryType
 entities.py # Brewery, BreweryAggregate
 validators.py # BreweryValidator, LocationValidator, ContactValidator
 exceptions.py # 7 domain-specific exceptions
```

---

## Design Principles

### DDD (Domain-Driven Design)

| Concept | Implementation | File |
|---------|----------------|------|
| **Value Object** | `Coordinates`, `Address` | `value_objects.py` |
| **Entity** | `Brewery` | `entities.py` |
| **Aggregate** | `BreweryAggregate` | `entities.py` |
| **Factory** | `.from_dict()` methods | `entities.py` |
| **Validator** | `BreweryValidator` | `validators.py` |

### Clean Architecture Rules

 **Domain depends on NOTHING** 
 No imports of: `use_cases`, `repositories`, `services`, `config`

 **Business rules in domain** 
 No business logic in services/repositories

 **Rich domain model** 
 No anemic domain (DTOs only)

---

## Tips

!!! tip "Factory Methods"
 Always use `.from_dict()` for safe entity creation:
 ```python
 # Safe - validates data
 brewery = Brewery.from_dict(raw_data)

 # Unsafe - no validation
 brewery = Brewery(**raw_data)
 ```

!!! warning "Immutability"
 Value Objects are frozen - create new instances:
 ```python
 # Can't modify
 coords.latitude = 50.0 # Error!

 # Create new
 new_coords = Coordinates(50.0, coords.longitude)
 ```

!!! success "Quality Scoring"
 Use aggregate for complex business logic:
 ```python
 aggregate = BreweryAggregate(brewery)
 quality = aggregate.calculate_quality_score()

 if quality < 0.7:
 raise LowQualityDataError(...)
 ```

---

## References

- **Code**: `dags/domain/`
- **API Reference**: Use `help(Brewery)` in Python
- **Use Cases**: See [Use Cases Layer](use-cases.md)
- **Repositories**: See [Repository Pattern](repositories.md)

