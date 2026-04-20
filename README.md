# IHW Django Web Application

Web interface for the International Halley Watch (IHW) archive — metadata search across 9 scientific disciplines that observed Halley's Comet during 1985-1986.

## Quick Start

### Setup

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run development server
cd IHWApp
python manage.py runserver
```

Visit http://127.0.0.1:8000/

### Project Status

Currently: Fresh Django 6.0.4 installation. Database models and views not yet implemented.

See `IHW.plan` for project context and goals.

## Documentation

See `.github/copilot-instructions.md` for:
- Database architecture (39 tables, legacy MariaDB schema)
- Development commands and conventions
- Schema integration strategy

## Database

The database schema is defined in `ihwdb2-schema-latest.sql` (MariaDB dump).

**Important:** Django models will be generated from this existing schema using `inspectdb`, not created via migrations.

Data files are stored at `/data/working/IHWv2/data`.
