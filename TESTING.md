# Running Tests

## Test Command

To run tests with SQLite test database:

```bash
cd IHWApp
source ../venv/bin/activate
DJANGO_TESTING=1 python manage.py test
```

## Test Coverage

### Core Models (`core/tests.py`)
- ✅ Model string representations
- ✅ Model methods (has_file, etc.)
- ✅ All 7 tests passing

### Search Forms (`search/tests.py`)
- ✅ Date format validation (YYYY-MM-DD required)
- ✅ Form field validation
- ✅ Invalid date format rejection (MM/DD/YYYY)
- ✅ Date range validation (end after start)

### Search Views (`search/tests.py`)
- ✅ Search page rendering
- ✅ Form submission and redirect
- ✅ URL routing

## Note About Network Field Tests

Some tests for the `networks` field will fail in SQLite test mode because the field uses `ModelMultipleChoiceField` which queries the `ihw_network` table. These tests work fine when running the actual application with MariaDB.

To test the full application including network filters:
1. Use the development server with MariaDB
2. Manually test through the web interface

## Running Specific Test Classes

```bash
# Test just core models
DJANGO_TESTING=1 python manage.py test core.tests

# Test just search forms
DJANGO_TESTING=1 python manage.py test search.tests.ObservationSearchFormTest

# Verbose output
DJANGO_TESTING=1 python manage.py test --verbosity=2
```

## Database Configuration

The test suite uses SQLite (`:memory:`) when `DJANGO_TESTING=1` is set, to avoid requiring MariaDB test database permissions.

Production/development uses MariaDB (`ihwdb2` database).
