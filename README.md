# winidjango

(This project uses [pyrig](https://github.com/Winipedia/pyrig))


## Overview

**winidjango** is a production-ready Django utilities library that simplifies complex database operations and provides structured patterns for data management tasks. Built with type safety and performance in mind, it leverages modern Python features and integrates seamlessly with Django's ORM.

## Features

### Database Utilities (`winidjango.src.db`)

High-performance database operations with automatic optimization, dependency management, and type safety.

#### Bulk Operations (`bulk.py`)

Efficiently process large datasets with automatic chunking, multithreading, and transaction management.

**Core Functions:**

**`bulk_create_in_steps(model, bulk, step=1000)`**
- Creates thousands of model instances in configurable batches (default: 1000)
- Uses multithreading for parallel processing across chunks
- Returns list of created instances with populated PKs
- Wrapped in atomic transactions for data integrity

**`bulk_update_in_steps(model, bulk, update_fields, step=1000)`**
- Updates large datasets efficiently in batches
- Requires explicit `update_fields` list for safety
- Returns total count of updated objects
- Multithreaded processing for maximum performance

**`bulk_delete_in_steps(model, bulk, step=1000)`**
- Deletes in batches with cascade tracking
- Returns tuple: `(total_count, {model_name: count})`
- Tracks all cascade deletions across related models
- Safe handling of foreign key constraints

**`bulk_create_bulks_in_steps(bulk_by_class, step=1000)`**
- **Automatic Dependency Resolution**: Creates multiple model types in correct order
- Uses topological sorting to handle foreign key relationships
- Accepts dict mapping model classes to instance lists
- Returns dict with created instances (PKs populated)

**Advanced Comparison & Simulation:**

**`get_differences_between_bulks(bulk1, bulk2, fields)`**
- Compares two bulks by hashing field values
- Returns 4-tuple: `(in_1_not_2, in_2_not_1, in_both_from_1, in_both_from_2)`
- Useful for sync operations and change detection
- Preserves original object references

**`simulate_bulk_deletion(model_class, entries)`**
- **Preview deletions without executing** using Django's Collector
- Returns dict mapping models to objects that would be deleted
- Includes all cascade deletions
- Perfect for "what-if" analysis before destructive operations

**`multi_simulate_bulk_deletion(entries)`**
- Simulates deletions across multiple model types
- Aggregates cascade effects into single summary
- Accepts dict of `{model_class: [instances]}`

**Usage Examples:**

```python
from winidjango.src.db.bulk import (
    bulk_create_in_steps,
    bulk_create_bulks_in_steps,
    get_differences_between_bulks,
    simulate_bulk_deletion,
)

# Create 10,000 objects in batches of 1000
authors = [Author(name=f"Author {i}") for i in range(10000)]
created = bulk_create_in_steps(Author, authors, step=1000)
# Uses multithreading: ~10x faster than individual saves

# Create related models in dependency order
books = [Book(title=f"Book {i}", author=author) for i, author in enumerate(created)]
reviews = [Review(book=book, rating=5) for book in books]

results = bulk_create_bulks_in_steps({
    Author: authors,
    Book: books,      # Created after Author (foreign key dependency)
    Review: reviews,  # Created after Book (foreign key dependency)
})
# Automatically sorted: Author → Book → Review

# Compare two datasets
from winidjango.src.db.fields import get_fields
fields = get_fields(Author)
old_authors = Author.objects.all()
new_authors = [Author(name=f"Updated {i}") for i in range(100)]

to_delete, to_create, unchanged_old, unchanged_new = get_differences_between_bulks(
    list(old_authors), new_authors, fields
)

# Preview deletion impact
deletion_preview = simulate_bulk_deletion(Author, to_delete)
# Returns: {Author: {<Author: 1>, <Author: 2>}, Book: {<Book: 1>, <Book: 2>}, ...}
print(f"Would delete {len(deletion_preview[Author])} authors")
print(f"Would cascade delete {len(deletion_preview[Book])} books")
```

**Key Features:**
- **Multithreading**: Parallel processing of chunks for maximum speed
- **Transaction Safety**: Atomic operations with nested transaction warnings
- **Configurable Batch Size**: Default 1000, adjustable per operation
- **Type-Safe**: Full generic type hints with overloads
- **Memory Efficient**: Processes data in chunks, not all at once

#### Model Utilities (`models.py`)

**`topological_sort_models(models)`**
- Sorts models by foreign key dependencies using Python's `graphlib.TopologicalSorter`
- Ensures correct creation/deletion order
- Ignores self-referential relationships
- Raises `CycleError` for circular dependencies

**`hash_model_instance(instance, fields)`**
- Hashes model instances for comparison
- PK-based for saved instances (fast)
- Field-based for unsaved instances (content comparison)
- Used internally by `get_differences_between_bulks()`

**`BaseModel`** - Abstract base model with common fields:
- `created_at` - Auto-populated on creation
- `updated_at` - Auto-updated on save
- `meta` property - Type-safe access to `_meta`
- Custom `__str__()` and `__repr__()`

```python
from winidjango.src.db.models import BaseModel

class MyModel(BaseModel):
    name = models.CharField(max_length=100)

    class Meta(BaseModel.Meta):
        db_table = "my_model"

# Automatically includes created_at and updated_at
obj = MyModel.objects.create(name="test")
print(obj.created_at)  # datetime
print(obj)  # "MyModel(1)"
```

#### Field Utilities (`fields.py`)

**`get_fields(model)`** - Get all fields including relationships
**`get_field_names(fields)`** - Extract field names from field objects
**`get_model_meta(model)`** - Type-safe access to model `_meta`

```python
from winidjango.src.db.fields import get_fields, get_field_names

fields = get_fields(User)
field_names = get_field_names(fields)
# ['id', 'username', 'email', 'groups', 'user_permissions', ...]
```

#### SQL Utilities (`sql.py`)

**`execute_sql(sql, params=None)`**
- Execute raw SQL with safe parameter binding
- Returns tuple: `(column_names, rows)`
- Automatic cursor management
- Protection against SQL injection

```python
from winidjango.src.db.sql import execute_sql

columns, rows = execute_sql(
    "SELECT id, username FROM auth_user WHERE is_active = %(active)s",
    params={"active": True}
)
# columns: ['id', 'username']
# rows: [(1, 'admin'), (2, 'user'), ...]
```

### Management Commands (`winidjango.src.commands`)

A powerful framework for building Django management commands with built-in best practices, automatic logging, and standardized argument handling.

#### `ABCBaseCommand` - Base Command Framework

Abstract base class that provides a robust foundation for all Django management commands:

**Key Features:**
- **Template Method Pattern**: Enforces consistent command structure while allowing customization
- **Automatic Logging**: All method calls are logged with performance tracking via `ABCLoggingMixin`
- **Built-in Common Arguments**: Pre-configured standard options available to all commands:
  - `--dry_run` - Preview changes without executing
  - `--force` - Force execution of actions
  - `--delete` - Enable deletion operations
  - `--yes` - Auto-confirm all prompts
  - `--timeout` - Set command timeout
  - `--batch_size` - Configure batch processing size
  - `--threads` - Control thread count for parallel processing
  - `--processes` - Control process count for multiprocessing
- **Type-Safe**: Full type hints with abstract method enforcement at compile-time
- **Structured Execution Flow**: Separates common setup (`base_handle`) from command-specific logic (`handle_command`)

**Usage Pattern:**
```python
from winidjango.src.commands.base.base import ABCBaseCommand
from argparse import ArgumentParser

class MyCommand(ABCBaseCommand):
    def add_command_arguments(self, parser: ArgumentParser) -> None:
        """Add command-specific arguments."""
        parser.add_argument('--input-file', type=str, required=True)
        parser.add_argument('--output-format', choices=['json', 'csv'])

    def handle_command(self) -> None:
        """Execute command logic."""
        input_file = self.get_option('input_file')
        dry_run = self.get_option('dry_run')  # Built-in argument
        batch_size = self.get_option('batch_size')  # Built-in argument

        if dry_run:
            self.stdout.write('Dry run mode - no changes will be made')

        # Your command logic here
        self.process_data(input_file, batch_size)
```

#### `ImportDataBaseCommand` - Data Import Framework

Specialized command for structured data import workflows with automatic cleaning and bulk creation:

**Workflow Steps:**
1. **Import** (`handle_import()`) - Fetch raw data from any source, returns Polars DataFrame
2. **Clean** (`get_cleaning_df_cls()`) - Define data cleaning logic using `winiutils.CleaningDF`
3. **Transform** (`get_bulks_by_model()`) - Convert cleaned DataFrame to Django model instances
4. **Load** (`import_to_db()`) - Bulk create with automatic dependency resolution via topological sorting

**Key Features:**
- **Polars Integration**: High-performance data processing with Polars DataFrames
- **Automatic Cleaning**: Leverages `winiutils.CleaningDF` for standardized data cleaning pipeline
- **Dependency-Aware**: Uses `bulk_create_bulks_in_steps()` to handle foreign key relationships automatically
- **Inherits All Base Features**: Gets all `ABCBaseCommand` functionality (logging, common args, etc.)

**Usage Pattern:**
```python
from winidjango.src.commands.import_data import ImportDataBaseCommand
from winiutils.src.data.dataframe.cleaning import CleaningDF
import polars as pl

class MyCleaningDF(CleaningDF):
    """Define your data cleaning rules."""
    NAME_COL = "name"
    EMAIL_COL = "email"

    @classmethod
    def get_rename_map(cls) -> dict[str, str]:
        return {"name": "user_name", "email": "user_email"}

    @classmethod
    def get_col_dtype_map(cls) -> dict[str, type[pl.DataType]]:
        return {cls.NAME_COL: pl.Utf8, cls.EMAIL_COL: pl.Utf8}

    # ... other cleaning methods

class ImportUsersCommand(ImportDataBaseCommand):
    def handle_import(self) -> pl.DataFrame:
        """Fetch data from source."""
        return pl.read_csv("users.csv")

    def get_cleaning_df_cls(self) -> type[CleaningDF]:
        """Return your cleaning class."""
        return MyCleaningDF

    def get_bulks_by_model(self, df: pl.DataFrame) -> dict[type[Model], Iterable[Model]]:
        """Convert cleaned data to model instances."""
        users = [User(name=row["name"], email=row["email"])
                 for row in df.iter_rows(named=True)]
        profiles = [Profile(user=user) for user in users]

        # Automatically created in correct order (User before Profile)
        return {User: users, Profile: profiles}
```

**Benefits:**
- **Standardized Import Process**: Consistent pattern across all data import commands
- **Separation of Concerns**: Import, cleaning, and transformation logic clearly separated
- **Automatic Optimization**: Bulk operations with multithreading and dependency resolution
- **Data Quality**: Built-in cleaning pipeline ensures data consistency
- **Testable**: Each step can be tested independently
