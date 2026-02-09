# Database Utilities

The `winidjango.src.db` package provides high-performance database utilities
for Django applications, including bulk operations, model utilities,
field introspection, and raw SQL execution.

## Table of Contents

- [Bulk Operations](#bulk-operations)
- [Model Utilities](#model-utilities)
- [Field Utilities](#field-utilities)
- [SQL Utilities](#sql-utilities)

## Bulk Operations

Module: `winidjango.src.db.bulk`

High-performance bulk operations with automatic chunking, multithreading,
and transaction management.

### Core Functions

#### `bulk_create_in_steps()`

Create thousands of model instances efficiently in configurable batches.

**Signature:**

```python
def bulk_create_in_steps[TModel: Model](
    model: type[TModel],
    bulk: Iterable[TModel],
    step: int = 1000,
) -> list[TModel]:
    ...
```

**Parameters:**

- `model`: Django model class to create instances of
- `bulk`: Iterable of model instances to create
- `step`: Batch size (default: 1000)

**Returns:**

- List of created model instances with populated primary keys

**Features:**

- Multithreaded processing of chunks
- Atomic transaction wrapping
- Memory-efficient chunking
- Type-safe with generics

**Example:**

```python
from winidjango.src.db.bulk import bulk_create_in_steps

# Create 10,000 authors in batches of 1,000
authors = [Author(name=f"Author {i}") for i in range(10000)]
created = bulk_create_in_steps(Author, authors, step=1000)

print(f"Created {len(created)} authors")
print(f"First author PK: {created[0].pk}")
```

**Performance:**

- ~5-10x faster than individual `save()` calls
- Processes batches in parallel threads
- Minimal memory footprint

---

#### `bulk_update_in_steps()`

Update large datasets efficiently in batches.

**Signature:**

```python
def bulk_update_in_steps[TModel: Model](
    model: type[TModel],
    bulk: Iterable[TModel],
    update_fields: list[str],
    step: int = 1000,
) -> int:
    ...
```

**Parameters:**

- `model`: Django model class
- `bulk`: Iterable of model instances to update
- `update_fields`: List of field names to update (required for safety)
- `step`: Batch size (default: 1000)

**Returns:**

- Total count of updated objects

**Example:**

```python
from winidjango.src.db.bulk import bulk_update_in_steps

# Update 10,000 authors
authors = Author.objects.all()
for author in authors:
    author.name = author.name.upper()

updated_count = bulk_update_in_steps(
    Author, 
    authors, 
    update_fields=['name'],
    step=1000
)

print(f"Updated {updated_count} authors")
```

**Important:**

- Must specify `update_fields` explicitly for safety
- Only specified fields are updated in the database
- Objects must have primary keys (must be saved first)

---

#### `bulk_delete_in_steps()`

Delete model instances in batches with cascade tracking.

**Signature:**

```python
def bulk_delete_in_steps[TModel: Model](
    model: type[TModel],
    bulk: Iterable[TModel],
    step: int = 1000,
) -> tuple[int, dict[str, int]]:
    ...
```

**Parameters:**

- `model`: Django model class
- `bulk`: Iterable of model instances to delete
- `step`: Batch size (default: 1000)

**Returns:**

- Tuple of `(total_count, count_by_model_dict)`
  - `total_count`: Total number of objects deleted
  - `count_by_model_dict`: Dictionary mapping model names to deletion counts

**Example:**

```python
from winidjango.src.db.bulk import bulk_delete_in_steps

authors = Author.objects.filter(name__startswith="Test")
total, by_model = bulk_delete_in_steps(Author, list(authors), step=500)

print(f"Deleted {total} objects total")
for model_name, count in by_model.items():
    print(f"  {model_name}: {count}")
```

**Features:**

- Tracks cascade deletions across related models
- Safe handling of foreign key constraints
- Respects Django's `on_delete` behavior

---

#### `bulk_create_bulks_in_steps()`

Create multiple model types in correct dependency order automatically.

**Signature:**

```python
def bulk_create_bulks_in_steps[TModel: Model](
    bulk_by_class: dict[type[TModel], Iterable[TModel]],
    step: int = 1000,
) -> dict[type[TModel], list[TModel]]:
    ...
```

**Parameters:**

- `bulk_by_class`: Dictionary mapping model classes to iterables of instances
- `step`: Batch size (default: 1000)

**Returns:**

- Dictionary mapping model classes to lists of created instances

**Features:**

- **Automatic topological sorting** based on foreign key dependencies
- Creates models in correct order to avoid integrity errors
- Handles complex dependency graphs
- Returns all created instances with populated PKs

**Example:**

```python
from winidjango.src.db.bulk import bulk_create_bulks_in_steps

# Create related models - order doesn't matter!
authors = [Author(name=f"Author {i}") for i in range(100)]
books = [Book(title=f"Book {i}", author=authors[
    i % len(authors)]) for i in range(500)
]
reviews = [Review(book=books[i % len(books)], rating=5) for i in range(1000)]

# Provide in any order - library sorts by dependencies
results = bulk_create_bulks_in_steps({
    Review: reviews,      # Depends on Book
    Book: books,          # Depends on Author
    Author: authors,      # No dependencies
})

# Created in order: Author → Book → Review
print(f"Created {len(results[Author])} authors")
print(f"Created {len(results[Book])} books")
print(f"Created {len(results[Review])} reviews")
```

**How it works:**

1. Analyzes foreign key relationships between provided models
2. Uses `graphlib.TopologicalSorter` to determine creation order
3. Creates each model type in dependency order
4. Ignores self-referential relationships
5. Raises `CycleError` if circular dependencies detected

---

### Advanced Functions

#### `get_differences_between_bulks()`

Compare two bulks of model instances and return their differences.

**Signature:**

```python
def get_differences_between_bulks(
    bulk1: list[Model],
    bulk2: list[Model],
    fields: list[Field | ForeignObjectRel | GenericForeignKey],
) -> tuple[list[Model], list[Model], list[Model], list[Model]]:
    ...
```

**Parameters:**

- `bulk1`: First list of model instances
- `bulk2`: Second list of model instances
- `fields`: List of fields to compare (get with `get_fields()`)

**Returns:**

- 4-tuple of:
  1. Objects in `bulk1` but not in `bulk2`
  2. Objects in `bulk2` but not in `bulk1`
  3. Objects in both (from `bulk1`)
  4. Objects in both (from `bulk2`)

**Example:**

```python
from winidjango.src.db.bulk import get_differences_between_bulks
from winidjango.src.db.fields import get_fields

# Compare current database state with new data
current_users = list(User.objects.all())
new_users = [
    User(username=f"user_{i}", email=f"user_{i}@example.com") 
    for i in range(100)
    ]

fields = get_fields(User) to_delete, to_create, unchanged_old, unchanged_new =
get_differences_between_bulks(
    current_users, new_users, fields
)

print(f"To delete: {len(to_delete)}")
print(f"To create: {len(to_create)}")
print(f"Unchanged: {len(unchanged_old)}")

# Perform sync
if to_delete:
    bulk_delete_in_steps(User, to_delete)
if to_create:
    bulk_create_in_steps(User, to_create)
```

**Use Cases:**

- Data synchronization
- Change detection
- Incremental updates
- Audit trails

**How it works:**

- Hashes instances based on field values
- For saved instances: uses primary key
- For unsaved instances: uses field values
- Preserves original object references

---

#### `simulate_bulk_deletion()`

Preview what objects would be deleted without actually deleting them.

**Signature:**

```python
def simulate_bulk_deletion(
    model_class: type[Model],
    entries: list[Model],
) -> dict[type[Model], set[Model]]:
    ...
```

**Parameters:**

- `model_class`: Django model class of entries to delete
- `entries`: List of model instances to simulate deletion for

**Returns:**

- Dictionary mapping model classes to sets of objects that would be deleted

**Example:**

```python
from winidjango.src.db.bulk import simulate_bulk_deletion, bulk_delete_in_steps

# Get authors to potentially delete
authors = Author.objects.filter(name__startswith="Test")

# Preview deletion impact
deletion_preview = simulate_bulk_deletion(Author, list(authors))

# Show what would be deleted
print("Deletion preview:")
for model, objects in deletion_preview.items():
    print(f"  {model.__name__}: {len(objects)} objects")

# Example output:
#   Author: 10 objects
#   Book: 45 objects (cascade)
#   Review: 230 objects (cascade)

# Confirm with user
if input("Proceed? (y/n): ").lower() == 'y':
    total, by_model = bulk_delete_in_steps(Author, list(authors))
    print(f"Deleted {total} objects")
```

**Features:**

- Uses Django's `Collector` for accurate cascade simulation
- No database modifications
- Shows all cascade effects
- Respects `on_delete` settings

**Best Practice:**
Always simulate deletions before executing them,
especially for models with many relationships.

---

#### `multi_simulate_bulk_deletion()`

Simulate deletion for multiple model types and aggregate results.

**Signature:**

```python
def multi_simulate_bulk_deletion(
    entries: dict[type[Model], list[Model]],
) -> dict[type[Model], set[Model]]:
    ...
```

**Parameters:**

- `entries`: Dictionary mapping model classes to lists of instances

**Returns:**

- Dictionary mapping model classes to sets of all objects that would be deleted

**Example:**

```python
from winidjango.src.db.bulk import multi_simulate_bulk_deletion

# Simulate deletion of multiple model types
deletion_preview = multi_simulate_bulk_deletion({
    Author: list(Author.objects.filter(name__startswith="Test")),
    Publisher: list(Publisher.objects.filter(active=False)),
})

# Aggregated results across all deletions
for model, objects in deletion_preview.items():
    print(f"{model.__name__}: {len(objects)} objects")
```

---

### Configuration

#### Batch Size

The default batch size is 1000, defined in `STANDARD_BULK_SIZE`.
Adjust based on:

**Small batch sizes (100-500):**

- Complex models with many fields
- Models with heavy validation logic
- Limited memory environments
- High database load

**Large batch sizes (2000-5000):**

- Simple models with few fields
- No validation overhead
- Ample memory available
- Low database load

**Example:**

```python
# Small objects, large batches
bulk_create_in_steps(SimpleModel, objects, step=5000)

# Complex objects, small batches
bulk_create_in_steps(ComplexModel, objects, step=100)
```

---

### Performance Characteristics

#### Multithreading

All bulk operations use multithreading by default:

```python
# 10,000 objects, batch size 1,000 = 10 chunks
# Each chunk processed in parallel thread
bulk_create_in_steps(Model, objects, step=1000)
```

**Performance gain:** ~5-10x faster than sequential processing

#### Memory Usage

Memory usage is proportional to batch size, not total dataset size:

```python
# Only 1,000 objects in memory at a time
# Even when processing millions
bulk_create_in_steps(Model, huge_iterator, step=1000)
```

#### Transaction Overhead

Each bulk operation is wrapped in a transaction:

```python
@transaction.atomic  # DON'T add this
def my_function():
    bulk_create_in_steps(...)  # Already atomic
```

**Warning:** Nested transactions can cause issues.
Remove outer `@transaction.atomic` decorators.

---

## Model Utilities

Module: `winidjango.src.db.models`

Utilities for working with Django models,
including dependency sorting and hashing.

### Functions

#### `topological_sort_models()`

Sort Django models by foreign key dependencies.

**Signature:**

```python
def topological_sort_models[TModel: Model](
    models: list[type[TModel]],
) -> list[type[TModel]]:
    ...
```

**Parameters:**

- `models`: List of Django model classes to sort

**Returns:**

- List of models sorted in dependency order (dependencies first)

**Example:**

```python
from winidjango.src.db.models import topological_sort_models

# Unsorted models
models = [Review, Book, Author, Publisher]

# Sort by dependencies
sorted_models = topological_sort_models(models)
# Result: [Author, Publisher, Book, Review]

# Use for creation order
for model in sorted_models:
    # Create instances of model
    pass
```

**Features:**

- Uses Python's `graphlib.TopologicalSorter`
- Handles complex dependency graphs
- Ignores self-referential relationships
- Raises `CycleError` for circular dependencies

**Use Cases:**

- Determining creation order for related models
- Planning deletion order (reverse the list)
- Database migration ordering
- Fixture loading

---

#### `hash_model_instance()`

Generate a hash for a model instance based on its field values.

**Signature:**

```python
def hash_model_instance(
    instance: Model,
    fields: list[Field | ForeignObjectRel | GenericForeignKey],
) -> int:
    ...
```

**Parameters:**

- `instance`: Django model instance to hash
- `fields`: List of fields to include in hash

**Returns:**

- Integer hash value

**Example:**

```python
from winidjango.src.db.models import hash_model_instance
from winidjango.src.db.fields import get_fields

user = User(username="john", email="john@example.com")
fields = get_fields(User)
hash_value = hash_model_instance(user, fields)

# Same field values = same hash
user2 = User(username="john", email="john@example.com")
hash_value2 = hash_model_instance(user2, fields)
assert hash_value == hash_value2
```

**Behavior:**

- **Saved instances** (with PK): Hash based on primary key only
- **Unsaved instances** (no PK): Hash based on field values

**Use Cases:**

- Comparing model instances
- Detecting duplicates
- Change detection
- Used internally by `get_differences_between_bulks()`

**Warning:**
Not cryptographically secure. Use only for comparison purposes.

---

### Classes

#### `BaseModel`

Abstract base model with common fields and utilities.

**Fields:**

- `created_at`: DateTimeField, auto-populated on creation
- `updated_at`: DateTimeField, auto-updated on save

**Properties:**

- `meta`: Type-safe access to model's `_meta` attribute

**Methods:**

- `__str__()`: Returns `"ModelName(pk)"`
- `__repr__()`: Same as `__str__()`

**Example:**

```python
from winidjango.src.db.models import BaseModel
from django.db import models

class Article(BaseModel):
    title = models.CharField(max_length=200)
    content = models.TextField()

    class Meta(BaseModel.Meta):
        db_table = "articles"

# Automatically includes created_at and updated_at
article = Article.objects.create(title="Hello", content="World")
print(article.created_at)  # 2024-01-01 12:00:00
print(article.updated_at)  # 2024-01-01 12:00:00
print(article)  # "Article(1)"

# Update automatically updates updated_at
article.title = "Updated"
article.save()
print(article.updated_at)  # 2024-01-01 12:05:00
```

**Benefits:**

- Consistent timestamp tracking across all models
- Type-safe meta access
- Standardized string representation
- Reduces boilerplate code

**Note:**
Must inherit `BaseModel.Meta`
in your model's Meta class to maintain abstract status.

---

## Field Utilities

Module: `winidjango.src.db.fields`

Utilities for introspecting and working with Django model fields.

### Functions

#### `get_fields()`

Get all fields from a Django model including relationships.

**Signature:**

```python
def get_fields[TModel: Model](
    model: type[TModel],
) -> list[Field | ForeignObjectRel | GenericForeignKey]:
    ...
```

**Parameters:**

- `model`: Django model class

**Returns:**

- List of all field objects including:
  - Regular fields (CharField, IntegerField, etc.)
  - Foreign keys (ForeignKey, OneToOneField)
  - Reverse relationships (ForeignObjectRel)
  - Generic foreign keys (GenericForeignKey)

**Example:**

```python
from winidjango.src.db.fields import get_fields

fields = get_fields(User)
for field in fields:
    if hasattr(field, 'name'):
        print(f"{field.name}: {type(field).__name__}")

# Output:
# id: AutoField
# username: CharField
# email: EmailField
# groups: ManyToManyField
# ...
```

---

#### `get_field_names()`

Extract field names from a list of field objects.

**Signature:**

```python
def get_field_names(
    fields: list[Field | ForeignObjectRel | GenericForeignKey],
) -> list[str]:
    ...
```

**Parameters:**

- `fields`: List of field objects (from `get_fields()`)

**Returns:**

- List of field names as strings

**Example:**

```python
from winidjango.src.db.fields import get_fields, get_field_names

fields = get_fields(User)
field_names = get_field_names(fields)
print(field_names)
# ['id', 'username', 'email', 'first_name', 'last_name', ...]
```

---

#### `get_model_meta()`

Get the Django model metadata options object.

**Signature:**

```python
def get_model_meta(model: type[Model]) -> Options[Model]:
    ...
```

**Parameters:**

- `model`: Django model class

**Returns:**

- Model's `_meta` attribute (Options object)

**Example:**

```python
from winidjango.src.db.fields import get_model_meta

meta = get_model_meta(User)
print(meta.db_table)  # 'auth_user'
print(meta.app_label)  # 'auth'
print(meta.verbose_name)  # 'user'
```

**Use Cases:**

- Accessing model metadata
- Getting table name
- Inspecting model configuration
- Building dynamic queries

---

## SQL Utilities

Module: `winidjango.src.db.sql`

Utilities for executing raw SQL queries safely.

### Functions

#### `execute_sql()`

Execute raw SQL query with safe parameter binding.

**Signature:**

```python
def execute_sql(
    sql: str,
    params: dict[str, Any] | None = None,
) -> tuple[list[str], list[Any]]:
    ...
```

**Parameters:**

- `sql`: SQL query string (can contain parameter placeholders)
- `params`: Dictionary of parameters for safe binding (optional)

**Returns:**

- Tuple of `(column_names, rows)`
  - `column_names`: List of column names
  - `rows`: List of result rows (each row is a tuple)

**Example:**

```python
from winidjango.src.db.sql import execute_sql

# Simple query
columns, rows = execute_sql("SELECT id, username FROM auth_user LIMIT 10")
print(columns)  # ['id', 'username']
for row in rows:
    print(f"ID: {row[0]}, Username: {row[1]}")

# Query with parameters (safe from SQL injection)
columns, rows = execute_sql(
    "SELECT id, username FROM auth_user WHERE is_active = %(active)s",
    params={"active": True}
)

# Complex query
sql = """
    SELECT
        u.id,
        u.username,
        COUNT(a.id) as article_count
    FROM auth_user u
    LEFT JOIN articles a ON a.author_id = u.id
    WHERE u.date_joined >= %(since)s
    GROUP BY u.id, u.username
    ORDER BY article_count DESC
"""
columns, rows = execute_sql(sql, params={"since": "2024-01-01"})
```

**Features:**

- Automatic cursor management
- Safe parameter binding (prevents SQL injection)
- Returns column names for easy result processing
- Works with Django's default database connection

**Best Practices:**

- Always use parameter binding for user input
- Use Django ORM when possible
- Reserve for complex queries not expressible in ORM
- Consider using `raw()` for model-based queries

**Security:**

```python
# DON'T do this (SQL injection risk)
username = request.GET.get('username')
execute_sql(f"SELECT * FROM users WHERE username = '{username}'")

# DO this (safe parameter binding)
username = request.GET.get('username')
execute_sql(
    "SELECT * FROM users WHERE username = %(username)s",
    params={"username": username}
)
```

---

## Complete Example

Here's a complete example combining multiple utilities:

```python
from winidjango.src.db.bulk import (
    bulk_create_bulks_in_steps,
    simulate_bulk_deletion,
    bulk_delete_in_steps,
    get_differences_between_bulks,
)
from winidjango.src.db.fields import get_fields
from winidjango.src.db.models import BaseModel, topological_sort_models
from django.db import models

# Define models using BaseModel
class Author(BaseModel):
    name = models.CharField(max_length=100)

    class Meta(BaseModel.Meta):
        db_table = "authors"

class Book(BaseModel):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)

    class Meta(BaseModel.Meta):
        db_table = "books"

# Create data with automatic dependency resolution
authors = [Author(name=f"Author {i}") for i in range(100)]
books = [
    Book(title=f"Book {i}", author=authors[i % len(authors)]) 
    for i in range(500)
]

results = bulk_create_bulks_in_steps({
    Book: books,      # Provided in any order
    Author: authors,  # Library sorts by dependencies
})

print(f"Created {len(results[Author])} authors")
print(f"Created {len(results[Book])} books")

# Compare with new data
new_authors = [Author(name=f"Updated Author {i}") for i in range(50)]
fields = get_fields(Author)

to_delete, to_create, unchanged_old, unchanged_new =
get_differences_between_bulks(
    list(Author.objects.all()), new_authors, fields
)

# Preview deletion impact
if to_delete:
    deletion_preview = simulate_bulk_deletion(Author, to_delete)
    print("\nDeletion preview:")
    for model, objects in deletion_preview.items():
        print(f"  {model.__name__}: {len(objects)} objects")

    # Confirm and delete
    if input("Proceed? (y/n): ").lower() == 'y':
        total, by_model = bulk_delete_in_steps(Author, to_delete)
        print(f"\nDeleted {total} objects")

# Create new authors
if to_create:
    created = bulk_create_in_steps(Author, to_create)
    print(f"Created {len(created)} new authors")
```

---

## See Also

- **[Management Commands Documentation](commands.md)**
  - Command framework and data import
- **[Main Documentation](index.md)** - Overview and quick start
- **[Django Documentation](https://docs.djangoproject.com/)** -
Official Django docs
