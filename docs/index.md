# winidjango Documentation

Welcome to the **winidjango** documentation! This library provides production-ready utilities for Django applications, focusing on high-performance database operations and structured management command patterns.

## Overview

**winidjango** is designed to solve common Django development challenges:

- **Performance**: Bulk operations with multithreading for processing thousands of records efficiently
- **Safety**: Transaction management, deletion simulation, and type-safe APIs
- **Structure**: Standardized patterns for management commands and data imports
- **Developer Experience**: Full type hints, automatic logging, and comprehensive error handling

## Documentation

### Core Modules

- **[Database Utilities](db.md)** - High-performance bulk operations, model utilities, field introspection, and SQL helpers
  - Bulk create/update/delete operations
  - Automatic dependency resolution with topological sorting
  - Deletion simulation and bulk comparison
  - BaseModel abstract class
  - Field and SQL utilities

- **[Management Commands](commands.md)** - Command framework with automatic logging and structured data import
  - ABCBaseCommand template method pattern
  - ImportDataBaseCommand for data imports
  - Built-in arguments (dry-run, batch size, threading, etc.)
  - Complete examples and best practices

## Installation

```bash
pip install winidjango
```

Or using uv:

```bash
uv add winidjango
```

**Requirements:** Python 3.12+, Django, winiutils (auto-installed)

## Quick Start

### Bulk Create with Dependency Resolution

```python
from winidjango.src.db.bulk import bulk_create_bulks_in_steps

# Create related models - order doesn't matter!
authors = [Author(name=f"Author {i}") for i in range(100)]
books = [Book(title=f"Book {i}", author=authors[i]) for i in range(500)]

# Automatic dependency resolution
results = bulk_create_bulks_in_steps({
    Book: books,      # Depends on Author
    Author: authors,  # No dependencies
})
# Created in correct order: Author → Book
```

See **[Database Utilities](db.md)** for complete bulk operations documentation.

### Simulate Deletion

```python
from winidjango.src.db.bulk import simulate_bulk_deletion

# Preview cascade effects (no database changes)
authors = Author.objects.filter(name__startswith="Test")
deletion_preview = simulate_bulk_deletion(Author, list(authors))

# Show what would be deleted
for model, objects in deletion_preview.items():
    print(f"{model.__name__}: {len(objects)} objects")
```

See **[Database Utilities](db.md)** for deletion simulation details.

### Build Management Commands

```python
from winidjango.src.commands.base.base import ABCBaseCommand

class CleanupCommand(ABCBaseCommand):
    def add_command_arguments(self, parser):
        parser.add_argument('--days', type=int, default=30)

    def handle_command(self):
        days = self.get_option('days')
        dry_run = self.get_option('dry_run')  # Built-in

        # Your logic here
        if dry_run:
            self.stdout.write('Would delete X records')
        else:
            # Execute deletion
            pass
```

See **[Management Commands](commands.md)** for complete command framework documentation.

### Import Data from CSV

```python
from winidjango.src.commands.import_data import ImportDataBaseCommand
import polars as pl

class ImportUsersCommand(ImportDataBaseCommand):
    def handle_import(self) -> pl.DataFrame:
        return pl.read_csv(self.get_option('file'))

    def get_cleaning_df_cls(self):
        return UserCleaningDF  # Your cleaning rules

    def get_bulks_by_model(self, df):
        users = [User(username=row["username"]) for row in df.iter_rows(named=True)]
        return {User: users}
```

See **[Management Commands](commands.md)** for data import patterns.

## Key Features

- **High-Performance Bulk Operations** - Multithreaded processing with configurable batch sizes
- **Automatic Dependency Resolution** - Topological sorting for foreign key relationships
- **Deletion Simulation** - Preview cascade effects before executing
- **Dataset Comparison** - Detect differences and synchronize data
- **Management Command Framework** - Template method pattern with built-in arguments
- **Structured Data Import** - Polars integration with automatic cleaning
- **Type Safety** - Full type hints with Python 3.12+ generics

## Learn More

For detailed documentation, examples, and API reference:

- **[Database Utilities Documentation](db.md)** - Complete guide to bulk operations, model utilities, field introspection, and SQL helpers
- **[Management Commands Documentation](commands.md)** - Complete guide to command framework, data imports, and best practices

## External Resources

- **[GitHub Repository](https://github.com/Winipedia/winidjango)** - Source code and issue tracker
- **[Django Documentation](https://docs.djangoproject.com/)** - Official Django documentation
- **[winiutils](https://github.com/Winipedia/winiutils)** - General Python utilities
- **[Polars](https://pola.rs/)** - High-performance DataFrame library

---

**License**: MIT
