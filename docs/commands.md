# Management Commands

The `winidjango.src.commands` package provides a powerful framework for building Django management commands with built-in best practices, automatic logging, and standardized argument handling.

## Table of Contents

- [ABCBaseCommand](#abcbasecommand)
- [ImportDataBaseCommand](#importdatabasecommand)
- [Built-in Arguments](#built-in-arguments)
- [Best Practices](#best-practices)
- [Examples](#examples)

## ABCBaseCommand

Module: `winidjango.src.commands.base.base`

Abstract base class that provides a robust foundation for all Django management commands.

### Overview

`ABCBaseCommand` implements the **template method pattern** to enforce consistent command structure while allowing customization. It combines Django's `BaseCommand` with automatic logging and standardized argument handling.

**Key Features:**
- Template method pattern for consistent execution flow
- Automatic logging via `ABCLoggingMixin` from `winiutils`
- Built-in common arguments (dry-run, batch size, threading, etc.)
- Type-safe with full type hints
- Abstract method enforcement at compile-time

### Class Structure

```python
from winidjango.src.commands.base.base import ABCBaseCommand
from argparse import ArgumentParser

class MyCommand(ABCBaseCommand):
    """Your custom command."""
    
    def add_command_arguments(self, parser: ArgumentParser) -> None:
        """Add command-specific arguments."""
        # Implement your custom arguments
        pass
    
    def handle_command(self) -> None:
        """Execute command logic."""
        # Implement your command logic
        pass
```

### Abstract Methods

#### `add_command_arguments()`

Add command-specific arguments to the argument parser.

**Signature:**
```python
@abstractmethod
def add_command_arguments(self, parser: ArgumentParser) -> None:
    ...
```

**Parameters:**
- `parser`: Django's ArgumentParser instance

**Example:**
```python
def add_command_arguments(self, parser: ArgumentParser) -> None:
    parser.add_argument(
        '--input-file',
        type=str,
        required=True,
        help='Path to input file'
    )
    parser.add_argument(
        '--output-format',
        choices=['json', 'csv', 'xml'],
        default='json',
        help='Output format for results'
    )
    parser.add_argument(
        '--limit',
        type=int,
        help='Maximum number of records to process'
    )
```

---

#### `handle_command()`

Execute the command-specific logic.

**Signature:**
```python
@abstractmethod
def handle_command(self) -> None:
    ...
```

**Parameters:**
- None (access arguments via `self.get_option()`)

**Example:**
```python
def handle_command(self) -> None:
    # Get command-specific arguments
    input_file = self.get_option('input_file')
    output_format = self.get_option('output_format')
    limit = self.get_option('limit')
    
    # Get built-in arguments
    dry_run = self.get_option('dry_run')
    batch_size = self.get_option('batch_size') or 1000
    
    if dry_run:
        self.stdout.write(self.style.WARNING('DRY RUN MODE'))
    
    # Your command logic
    data = self.load_data(input_file, limit)
    self.process_data(data, batch_size, dry_run)
    self.export_results(output_format)
```

### Methods

#### `get_option()`

Get an option value from parsed command-line arguments.

**Signature:**
```python
def get_option(self, option: str) -> Any:
    ...
```

**Parameters:**
- `option`: Option name (use underscores, not hyphens)

**Returns:**
- Option value (type depends on argument definition)

**Example:**
```python
def handle_command(self) -> None:
    # Command-line: --input-file data.csv
    # Access as: input_file (underscores)
    input_file = self.get_option('input_file')
    
    # Built-in options
    dry_run = self.get_option('dry_run')  # bool
    batch_size = self.get_option('batch_size')  # int | None
    threads = self.get_option('threads')  # int | None
```

### Execution Flow

The command execution follows this flow:

1. **`handle()`** - Entry point (final, cannot override)
2. **`base_handle()`** - Common setup (stores args and options)
3. **`handle_command()`** - Your custom logic (abstract, must implement)

```python
# Automatic flow:
handle()
  ├─> base_handle(*args, **options)  # Stores self.args, self.options
  └─> handle_command()                # Your implementation
```

### Built-in Arguments

All commands inheriting from `ABCBaseCommand` automatically get these arguments:

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--dry_run` | bool | False | Preview changes without executing |
| `--force` | bool | False | Force execution of actions |
| `--delete` | bool | False | Enable deletion operations |
| `--yes` | bool | False | Auto-confirm all prompts |
| `--timeout` | int | None | Command timeout in seconds |
| `--batch_size` | int | None | Batch processing size |
| `--threads` | int | None | Thread count for parallel processing |
| `--processes` | int | None | Process count for multiprocessing |

**Access via Options class:**
```python
class MyCommand(ABCBaseCommand):
    def handle_command(self) -> None:
        # Using Options class constants
        dry_run = self.get_option(self.Options.DRY_RUN)
        batch_size = self.get_option(self.Options.BATCH_SIZE)
        threads = self.get_option(self.Options.THREADS)
```

### Complete Example

```python
from winidjango.src.commands.base.base import ABCBaseCommand
from argparse import ArgumentParser
from winidjango.src.db.bulk import bulk_create_in_steps

class ImportProductsCommand(ABCBaseCommand):
    """Import products from CSV file."""
    
    def add_command_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            '--file',
            type=str,
            required=True,
            help='Path to CSV file'
        )
        parser.add_argument(
            '--category',
            type=str,
            help='Filter by category'
        )
    
    def handle_command(self) -> None:
        file_path = self.get_option('file')
        category = self.get_option('category')
        dry_run = self.get_option('dry_run')
        batch_size = self.get_option('batch_size') or 1000
        
        self.stdout.write(f'Processing {file_path}')
        
        # Load data
        products = self.load_products(file_path, category)
        self.stdout.write(f'Loaded {len(products)} products')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - No changes made'))
            return
        
        # Create in database
        created = bulk_create_in_steps(Product, products, step=batch_size)
        self.stdout.write(
            self.style.SUCCESS(f'Created {len(created)} products')
        )
    
    def load_products(self, file_path: str, category: str | None) -> list[Product]:
        # Your loading logic
        pass
```

**Usage:**
```bash
# Dry run
python manage.py import_products --file products.csv --dry_run

# With batch size
python manage.py import_products --file products.csv --batch_size 500

# With category filter
python manage.py import_products --file products.csv --category electronics

# Force mode
python manage.py import_products --file products.csv --force
```

---

## ImportDataBaseCommand

Module: `winidjango.src.commands.import_data`

Specialized command for structured data import workflows with automatic cleaning and bulk creation.

### Overview

`ImportDataBaseCommand` extends `ABCBaseCommand` to provide a standardized 4-step workflow for data imports:

1. **Import** - Fetch raw data from source
2. **Clean** - Apply data cleaning rules
3. **Transform** - Convert to Django model instances
4. **Load** - Bulk create with dependency resolution

**Key Features:**
- Polars DataFrame integration for high-performance data processing
- Automatic data cleaning via `winiutils.CleaningDF`
- Dependency-aware bulk creation with topological sorting
- Inherits all `ABCBaseCommand` features (logging, built-in args, etc.)

### Abstract Methods

#### `handle_import()`

Fetch raw data from the source.

**Signature:**
```python
@abstractmethod
def handle_import(self) -> pl.DataFrame:
    ...
```

**Returns:**
- Polars DataFrame containing raw data

**Example:**
```python
import polars as pl

def handle_import(self) -> pl.DataFrame:
    file_path = self.get_option('file')
    
    # From CSV
    return pl.read_csv(file_path)
    
    # From JSON
    # return pl.read_json(file_path)
    
    # From database
    # return pl.read_database(query, connection)
    
    # From API
    # data = requests.get(api_url).json()
    # return pl.DataFrame(data)
```

---

#### `get_cleaning_df_cls()`

Return the data cleaning class.

**Signature:**
```python
@abstractmethod
def get_cleaning_df_cls(self) -> type[CleaningDF]:
    ...
```

**Returns:**
- Subclass of `winiutils.CleaningDF`

**Example:**
```python
from winiutils.src.data.dataframe.cleaning import CleaningDF
import polars as pl

class UserCleaningDF(CleaningDF):
    """Data cleaning rules for user import."""
    
    USERNAME_COL = "username"
    EMAIL_COL = "email"
    AGE_COL = "age"
    
    @classmethod
    def get_rename_map(cls) -> dict[str, str]:
        """Rename columns."""
        return {
            "user_name": cls.USERNAME_COL,
            "user_email": cls.EMAIL_COL,
        }
    
    @classmethod
    def get_col_dtype_map(cls) -> dict[str, type[pl.DataType]]:
        """Define column types."""
        return {
            cls.USERNAME_COL: pl.Utf8,
            cls.EMAIL_COL: pl.Utf8,
            cls.AGE_COL: pl.Int64,
        }
    
    @classmethod
    def get_no_null_cols(cls) -> tuple[str, ...]:
        """Columns that cannot be null."""
        return (cls.USERNAME_COL, cls.EMAIL_COL)
    
    @classmethod
    def get_unique_subsets(cls) -> tuple[tuple[str, ...], ...]:
        """Define uniqueness constraints."""
        return ((cls.USERNAME_COL,), (cls.EMAIL_COL,))

def get_cleaning_df_cls(self) -> type[CleaningDF]:
    return UserCleaningDF
```

---

#### `get_bulks_by_model()`

Convert cleaned DataFrame to Django model instances.

**Signature:**
```python
@abstractmethod
def get_bulks_by_model(
    self, df: pl.DataFrame
) -> dict[type[Model], Iterable[Model]]:
    ...
```

**Parameters:**
- `df`: Cleaned Polars DataFrame

**Returns:**
- Dictionary mapping model classes to iterables of instances

**Example:**
```python
def get_bulks_by_model(self, df: pl.DataFrame) -> dict[type[Model], Iterable[Model]]:
    # Convert DataFrame rows to model instances
    users = [
        User(
            username=row["username"],
            email=row["email"],
            age=row["age"]
        )
        for row in df.iter_rows(named=True)
    ]
    
    # Create related models
    profiles = [Profile(user=user) for user in users]
    
    # Return in any order - automatic dependency resolution
    return {
        User: users,
        Profile: profiles,  # Created after User
    }
```

### Methods

#### `import_to_db()`

Import cleaned data to database (called automatically).

**Signature:**
```python
def import_to_db(self) -> None:
    ...
```

**Behavior:**
- Calls `get_bulks_by_model()` to get model instances
- Uses `bulk_create_bulks_in_steps()` for dependency-aware creation
- Automatically sorts models by foreign key dependencies

**Note:** You typically don't override this method.

### Complete Example

```python
from winidjango.src.commands.import_data import ImportDataBaseCommand
from winiutils.src.data.dataframe.cleaning import CleaningDF
from argparse import ArgumentParser
import polars as pl

class ProductCleaningDF(CleaningDF):
    """Cleaning rules for product data."""
    
    NAME_COL = "name"
    PRICE_COL = "price"
    SKU_COL = "sku"
    
    @classmethod
    def get_col_dtype_map(cls) -> dict[str, type[pl.DataType]]:
        return {
            cls.NAME_COL: pl.Utf8,
            cls.PRICE_COL: pl.Float64,
            cls.SKU_COL: pl.Utf8,
        }
    
    @classmethod
    def get_no_null_cols(cls) -> tuple[str, ...]:
        return (cls.NAME_COL, cls.SKU_COL)
    
    @classmethod
    def get_unique_subsets(cls) -> tuple[tuple[str, ...], ...]:
        return ((cls.SKU_COL,),)

class ImportProductsCommand(ImportDataBaseCommand):
    """Import products from CSV with automatic cleaning."""
    
    def add_command_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument('--file', type=str, required=True)
        parser.add_argument('--category-id', type=int, required=True)
    
    def handle_import(self) -> pl.DataFrame:
        file_path = self.get_option('file')
        return pl.read_csv(file_path)
    
    def get_cleaning_df_cls(self) -> type[CleaningDF]:
        return ProductCleaningDF
    
    def get_bulks_by_model(self, df: pl.DataFrame) -> dict[type[Model], Iterable[Model]]:
        category_id = self.get_option('category_id')
        
        products = [
            Product(
                name=row["name"],
                price=row["price"],
                sku=row["sku"],
                category_id=category_id
            )
            for row in df.iter_rows(named=True)
        ]
        
        return {Product: products}
```

**Usage:**
```bash
# Import products
python manage.py import_products --file products.csv --category-id 5

# Dry run
python manage.py import_products --file products.csv --category-id 5 --dry_run

# With custom batch size
python manage.py import_products --file products.csv --category-id 5 --batch_size 500
```

---

## Built-in Arguments

### Detailed Reference

#### `--dry_run`

Preview changes without executing them.

**Type:** Boolean flag  
**Default:** False

**Example:**
```python
def handle_command(self) -> None:
    dry_run = self.get_option('dry_run')
    
    if dry_run:
        self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        # Show what would happen
        self.preview_changes()
        return
    
    # Actual execution
    self.execute_changes()
```

**Usage:**
```bash
python manage.py mycommand --dry_run
```

---

#### `--batch_size`

Configure batch processing size.

**Type:** Integer  
**Default:** None (use command's default)

**Example:**
```python
def handle_command(self) -> None:
    batch_size = self.get_option('batch_size') or 1000
    
    bulk_create_in_steps(Model, objects, step=batch_size)
```

**Usage:**
```bash
python manage.py mycommand --batch_size 500
```

---

#### `--threads`

Control thread count for parallel processing.

**Type:** Integer  
**Default:** None (use system default)

**Example:**
```python
def handle_command(self) -> None:
    threads = self.get_option('threads') or 4
    
    with ThreadPoolExecutor(max_workers=threads) as executor:
        executor.map(process_item, items)
```

**Usage:**
```bash
python manage.py mycommand --threads 8
```

---

#### `--force`

Force execution of actions (skip confirmations).

**Type:** Boolean flag  
**Default:** False

**Example:**
```python
def handle_command(self) -> None:
    force = self.get_option('force')
    
    if not force:
        confirm = input('Are you sure? (y/n): ')
        if confirm.lower() != 'y':
            self.stdout.write('Cancelled')
            return
    
    self.execute_dangerous_operation()
```

**Usage:**
```bash
python manage.py mycommand --force
```

---

#### `--delete`

Enable deletion operations.

**Type:** Boolean flag  
**Default:** False

**Example:**
```python
def handle_command(self) -> None:
    delete = self.get_option('delete')
    
    if delete:
        self.delete_old_records()
    else:
        self.stdout.write('Skipping deletion (use --delete to enable)')
```

**Usage:**
```bash
python manage.py mycommand --delete
```

---

#### `--yes`

Auto-confirm all prompts.

**Type:** Boolean flag  
**Default:** False

**Example:**
```python
def handle_command(self) -> None:
    yes = self.get_option('yes')
    
    if not yes:
        confirm = input('Proceed? (y/n): ')
        if confirm.lower() != 'y':
            return
    
    self.execute()
```

**Usage:**
```bash
python manage.py mycommand --yes
```

---

#### `--timeout`

Set command timeout in seconds.

**Type:** Integer  
**Default:** None (no timeout)

**Example:**
```python
import signal

def handle_command(self) -> None:
    timeout = self.get_option('timeout')
    
    if timeout:
        signal.alarm(timeout)
    
    try:
        self.long_running_operation()
    except TimeoutError:
        self.stdout.write(self.style.ERROR('Command timed out'))
```

**Usage:**
```bash
python manage.py mycommand --timeout 300  # 5 minutes
```

---

#### `--processes`

Control process count for multiprocessing.

**Type:** Integer  
**Default:** None (use system default)

**Example:**
```python
from multiprocessing import Pool

def handle_command(self) -> None:
    processes = self.get_option('processes') or 4
    
    with Pool(processes=processes) as pool:
        results = pool.map(process_item, items)
```

**Usage:**
```bash
python manage.py mycommand --processes 4
```

---

## Best Practices

### 1. Use Dry Run for Destructive Operations

```python
def handle_command(self) -> None:
    dry_run = self.get_option('dry_run')
    
    # Preview deletions
    if dry_run:
        preview = simulate_bulk_deletion(Model, objects)
        self.stdout.write(f'Would delete {len(preview)} objects')
        return
    
    # Actual deletion
    bulk_delete_in_steps(Model, objects)
```

### 2. Provide Progress Feedback

```python
def handle_command(self) -> None:
    total = len(items)
    
    for i, item in enumerate(items, 1):
        self.process_item(item)
        
        if i % 100 == 0:
            self.stdout.write(f'Processed {i}/{total} items')
    
    self.stdout.write(self.style.SUCCESS(f'Completed {total} items'))
```

### 3. Handle Errors Gracefully

```python
def handle_command(self) -> None:
    errors = []
    
    for item in items:
        try:
            self.process_item(item)
        except Exception as e:
            errors.append((item, str(e)))
            self.stdout.write(self.style.ERROR(f'Error processing {item}: {e}'))
    
    if errors:
        self.stdout.write(self.style.WARNING(f'{len(errors)} errors occurred'))
    else:
        self.stdout.write(self.style.SUCCESS('All items processed successfully'))
```

### 4. Use Batch Size Appropriately

```python
def handle_command(self) -> None:
    batch_size = self.get_option('batch_size')
    
    # Adjust based on object complexity
    if not batch_size:
        if self.is_complex_model():
            batch_size = 100
        else:
            batch_size = 1000
    
    bulk_create_in_steps(Model, objects, step=batch_size)
```

### 5. Leverage Built-in Arguments

```python
def handle_command(self) -> None:
    # Combine multiple built-in arguments
    dry_run = self.get_option('dry_run')
    force = self.get_option('force')
    batch_size = self.get_option('batch_size') or 1000
    
    if dry_run:
        self.preview()
        return
    
    if not force and not self.confirm():
        return
    
    self.execute(batch_size)
```

### 6. Document Your Commands

```python
class MyCommand(ABCBaseCommand):
    """
    Import users from CSV file.
    
    This command imports users from a CSV file with the following columns:
    - username: User's username (required)
    - email: User's email (required)
    - first_name: User's first name (optional)
    - last_name: User's last name (optional)
    
    Examples:
        # Basic import
        python manage.py import_users --file users.csv
        
        # Dry run
        python manage.py import_users --file users.csv --dry_run
        
        # With custom batch size
        python manage.py import_users --file users.csv --batch_size 500
    """
    
    help = "Import users from CSV file"
```

---

## Examples

### Example 1: Simple Data Processing Command

```python
from winidjango.src.commands.base.base import ABCBaseCommand
from argparse import ArgumentParser

class CleanupOldRecordsCommand(ABCBaseCommand):
    """Delete records older than specified days."""
    
    help = "Delete old records from database"
    
    def add_command_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Delete records older than this many days'
        )
        parser.add_argument(
            '--model',
            type=str,
            required=True,
            help='Model name to clean up'
        )
    
    def handle_command(self) -> None:
        from django.apps import apps
        from datetime import datetime, timedelta
        
        days = self.get_option('days')
        model_name = self.get_option('model')
        dry_run = self.get_option('dry_run')
        delete = self.get_option('delete')
        
        # Get model
        model = apps.get_model(model_name)
        
        # Calculate cutoff date
        cutoff = datetime.now() - timedelta(days=days)
        
        # Get old records
        old_records = model.objects.filter(created_at__lt=cutoff)
        count = old_records.count()
        
        self.stdout.write(f'Found {count} records older than {days} days')
        
        if not delete:
            self.stdout.write(self.style.WARNING('Use --delete to actually delete records'))
            return
        
        if dry_run:
            self.stdout.write(self.style.WARNING(f'DRY RUN: Would delete {count} records'))
            return
        
        # Delete
        deleted, _ = old_records.delete()
        self.stdout.write(self.style.SUCCESS(f'Deleted {deleted} records'))
```

### Example 2: Data Import with Validation

```python
from winidjango.src.commands.import_data import ImportDataBaseCommand
from winiutils.src.data.dataframe.cleaning import CleaningDF
from argparse import ArgumentParser
import polars as pl

class OrderCleaningDF(CleaningDF):
    ORDER_ID_COL = "order_id"
    CUSTOMER_ID_COL = "customer_id"
    AMOUNT_COL = "amount"
    
    @classmethod
    def get_col_dtype_map(cls) -> dict[str, type[pl.DataType]]:
        return {
            cls.ORDER_ID_COL: pl.Utf8,
            cls.CUSTOMER_ID_COL: pl.Int64,
            cls.AMOUNT_COL: pl.Float64,
        }
    
    @classmethod
    def get_no_null_cols(cls) -> tuple[str, ...]:
        return (cls.ORDER_ID_COL, cls.CUSTOMER_ID_COL, cls.AMOUNT_COL)

class ImportOrdersCommand(ImportDataBaseCommand):
    """Import orders with customer validation."""
    
    def add_command_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument('--file', type=str, required=True)
        parser.add_argument('--validate-customers', action='store_true')
    
    def handle_import(self) -> pl.DataFrame:
        return pl.read_csv(self.get_option('file'))
    
    def get_cleaning_df_cls(self) -> type[CleaningDF]:
        return OrderCleaningDF
    
    def get_bulks_by_model(self, df: pl.DataFrame) -> dict[type[Model], Iterable[Model]]:
        validate = self.get_option('validate_customers')
        
        # Validate customers exist
        if validate:
            customer_ids = df['customer_id'].to_list()
            existing = set(Customer.objects.filter(
                id__in=customer_ids
            ).values_list('id', flat=True))
            
            missing = set(customer_ids) - existing
            if missing:
                self.stdout.write(
                    self.style.ERROR(f'Missing customers: {missing}')
                )
                return {}
        
        # Create orders
        orders = [
            Order(
                order_id=row["order_id"],
                customer_id=row["customer_id"],
                amount=row["amount"]
            )
            for row in df.iter_rows(named=True)
        ]
        
        return {Order: orders}
```

### Example 3: Multi-Model Import

```python
from winidjango.src.commands.import_data import ImportDataBaseCommand
from winiutils.src.data.dataframe.cleaning import CleaningDF
import polars as pl

class StoreDataCleaningDF(CleaningDF):
    STORE_NAME_COL = "store_name"
    PRODUCT_NAME_COL = "product_name"
    PRICE_COL = "price"
    
    @classmethod
    def get_col_dtype_map(cls) -> dict[str, type[pl.DataType]]:
        return {
            cls.STORE_NAME_COL: pl.Utf8,
            cls.PRODUCT_NAME_COL: pl.Utf8,
            cls.PRICE_COL: pl.Float64,
        }

class ImportStoreDataCommand(ImportDataBaseCommand):
    """Import stores and their products."""
    
    def add_command_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument('--file', type=str, required=True)
    
    def handle_import(self) -> pl.DataFrame:
        return pl.read_csv(self.get_option('file'))
    
    def get_cleaning_df_cls(self) -> type[CleaningDF]:
        return StoreDataCleaningDF
    
    def get_bulks_by_model(self, df: pl.DataFrame) -> dict[type[Model], Iterable[Model]]:
        # Get unique stores
        store_names = df['store_name'].unique().to_list()
        stores = [Store(name=name) for name in store_names]
        
        # Create store name to instance mapping
        store_map = {store.name: store for store in stores}
        
        # Create products
        products = [
            Product(
                name=row["product_name"],
                price=row["price"],
                store=store_map[row["store_name"]]
            )
            for row in df.iter_rows(named=True)
        ]
        
        # Return both - automatic dependency resolution
        return {
            Store: stores,
            Product: products,  # Created after Store
        }
```

---

## See Also

- **[Database Utilities Documentation](db.md)** - Bulk operations and model utilities
- **[Main Documentation](index.md)** - Overview and quick start
- **[winiutils Documentation](https://github.com/Winipedia/winiutils)** - CleaningDF and other utilities
