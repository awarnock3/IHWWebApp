# IHW Django Web Application - Copilot Instructions

## Project Overview

This is a Django web application for the International Halley Watch (IHW) archive, containing metadata from 9 scientific disciplines that observed Halley's Comet during its 1985-1986 apparition. The goal is to provide a searchable interface to help scientists locate observation data files based on date, position, and distance from the sun.

**Key Context:**
- The database schema is **legacy** and **pre-existing** in MariaDB (see `ihwdb2-schema-latest.sql`)
- Django is being built **on top of** an existing relational schema (not using Django's ORM to create tables)
- Data files are stored locally at `/data/working/IHWv2/data`
- The project is designed for long-term preservation (targeting accessibility for scientists in 2061)

## Architecture

### Database Structure

The database has **39 tables** organized into three categories:

1. **Core Metadata Tables** (`idx_meta_*` - 26 tables)
   - `idx_meta_common`: Cross-discipline common metadata for ALL observations
     - Contains: discipline, date_obs, net_num, observer, filename
     - Primary key: `id`
     - Unique constraint: (`discipline`, `idxfileid`, `linenum`)
     - Foreign key to `ihw_files.fileid`
   - Discipline-specific tables (e.g., `idx_meta_amdr`, `idx_meta_lspn`, etc.)
     - Each has a foreign key `meta_common_id` → `idx_meta_common.id`
     - Contains FITS header metadata specific to each subdiscipline

2. **Master Reference Tables**
   - `ihw_network`: 9 scientific disciplines (Amateur, Astrometry, Infrared, etc.)
   - `ihw_subnet`: Subdisciplines within each network
     - Foreign key: `discipline` → `ihw_network.id`
   - `ihw_files`: Maps data files to networks/subnets
     - Primary key: `fileid`
     - Referenced by `idx_meta_common.idxfileid`

3. **Appendix Tables** (`apx_*` - 8 tables)
   - Observatory sites, country codes, observer information

### Schema-Django Integration Pattern

**DO NOT use `python manage.py migrate` to create tables** - they already exist in MariaDB.

Instead:
1. Use `python manage.py inspectdb` to generate Django models from the existing schema
2. Set `managed = False` in model Meta classes (Django won't try to create/alter tables)
3. Define relationships in Django models to match existing foreign keys

### Cross-Network Query Strategy

The primary use case is **cross-discipline search**. The `idx_meta_common` table is the hub:
- Every observation has an entry in `idx_meta_common`
- JOIN to discipline-specific `idx_meta_*` tables via `meta_common_id`
- JOIN to `ihw_network`/`ihw_subnet` for discipline filtering
- JOIN to `ihw_files` via `idxfileid` for file location

**Example query pattern:**
```sql
SELECT c.date_obs, c.observer, c.filename, n.name as network
FROM idx_meta_common c
JOIN ihw_network n ON c.discipline = n.discipline
WHERE c.date_obs BETWEEN '1985-01-01' AND '1986-12-31'
```

## Django Project Structure

```
IHWApp/
├── manage.py
└── IHWApp/          # Django project configuration
    ├── settings.py
    ├── urls.py
    ├── wsgi.py
    └── asgi.py
```

**Current state:** Django 6.0.4 installation with default settings.

**Database configuration:** Currently using SQLite (default). Needs to be configured for MariaDB connection.

## Development Commands

### Virtual Environment

The project uses a Python virtual environment in the `venv/` directory.

```bash
# Activate virtual environment (required before any Django commands)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Deactivate when done
deactivate
```

### Django Management

**All Django commands require the virtual environment to be activated first.**

```bash
# Working directory for all Django commands
cd IHWApp

# Run development server
python manage.py runserver

# Database inspection (generate models from existing schema)
python manage.py inspectdb > models_generated.py

# Database shell (connect to configured database)
python manage.py dbshell

# Django shell (Python REPL with Django environment)
python manage.py shell

# Run system checks
python manage.py check
```

### Testing

No test framework is currently configured.

### Dependencies

Dependencies are managed in `requirements.txt`:
- Django 6.0.4
- asgiref 3.11.1 (ASGI support)
- sqlparse 0.5.5 (SQL formatting)

## Key Conventions

### Legacy Database Compatibility

1. **Never use migrations to alter the schema**
   - The MariaDB schema is the source of truth
   - Django models should be read-only representations with `managed = False`

2. **Handle schema quirks**
   - Tables use mixed character sets (utf8mb3, utf8mb4)
   - Some tables have AUTO_INCREMENT primary keys (Django will handle with AutoField)
   - Foreign key constraints exist and must be respected

3. **Date/time handling**
   - `date_obs` is stored as `datetime` in MySQL
   - Django will need proper timezone configuration (currently `USE_TZ = True`, `TIME_ZONE = 'UTC'`)

### Naming Conventions

- **Database tables:** Use underscores (e.g., `idx_meta_common`, `ihw_network`)
- **Django models:** Follow Django conventions - class names in PascalCase will map to snake_case table names via `db_table` in Meta

### File Path Conventions

- Data files stored at `/data/working/IHWv2/data` (not in repository)
- Schema dump: `ihwdb2-schema-latest.sql` (in repository root, outside Django project)
- Project plan: `IHW.plan` (context document, not code)

## Important Constraints

1. **Networks and Subdisciplines**
   - 9 primary networks (disciplines)
   - Each network may have multiple subnets
   - Not all networks have subnets (relationship is optional)

2. **Observation Metadata Flow**
   - `idx_meta_common` is mandatory for every observation
   - Discipline-specific metadata in `idx_meta_*` tables is optional
   - A file in `ihw_files` may be referenced by multiple observations

3. **Search Priority**
   - Primary search dimensions: date, sky position (RA/DEC), solar distance
   - Must work across all 9 disciplines simultaneously
   - Performance matters - there are 332,405 entries in `idx_meta_common` alone

## Security Notes

- `SECRET_KEY` in settings.py is insecure and marked for development only
- `DEBUG = True` is set (do not deploy to production as-is)
- No database credentials are currently configured

## Data Archive Context

The 9 IHW disciplines (networks):
1. Amateur Observations (subnets: Drawings, Photography, Spectra, Visual)
2. Astrometry Observations
3. Infrared Observations (subnets: Magnitudes, Photometry, Polarimetry, Spectra)
4. Large-Scale Phenomena
5. Meteor Studies (subnets: Radar, Visual)
6. Near-Nucleus Studies
7. Photometry and Polarimetry Observations
8. Radio Observations (subnets: CN, OH, Radar, Spectral Line, UV)
9. Spectral Observations

Each discipline has its own metadata table (`idx_meta_*`) with domain-specific FITS header fields.
