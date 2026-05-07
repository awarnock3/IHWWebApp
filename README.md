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

## Apache deployment

This repository supports Apache + `mod_wsgi` deployment with runtime settings loaded from `/etc/ihwapp/ihwapp.env`. That keeps secrets out of the repo and makes it easier to move the app to another host.

The example layout below uses `/var/www/ihwapp` as the app root and serves the site at `http://localhost/ihwapp`:

```bash
# app tree expected by the provided Apache config
/var/www/ihwapp/
├── IHWApp/
│   ├── manage.py
│   ├── IHWApp/
│   └── staticfiles/
└── venv/
```

Use these files as the starting point:

- `.env.example` for required Django and MariaDB environment variables
- `deploy/apache/ihwapp.conf` for the Apache virtual host

Deployment checklist:

```bash
sudo apt install libapache2-mod-wsgi-py3 python3-venv rsync

sudo mkdir -p /var/www/ihwapp
sudo rsync -a --delete \
  --exclude '.git/' \
  --exclude 'venv/' \
  --exclude '__pycache__/' \
  --exclude 'IHWApp/staticfiles/' \
  /path/to/IHWDjango/ /var/www/ihwapp/

sudo python3 -m venv /var/www/ihwapp/venv
sudo /var/www/ihwapp/venv/bin/pip install --upgrade pip
sudo /var/www/ihwapp/venv/bin/pip install -r /var/www/ihwapp/requirements.txt

sudo install -d -m 0750 /etc/ihwapp
sudo install -m 0640 /var/www/ihwapp/.env.example /etc/ihwapp/ihwapp.env
sudo editor /etc/ihwapp/ihwapp.env

sudo install -m 0644 /var/www/ihwapp/deploy/apache/ihwapp.conf /etc/apache2/sites-available/ihwapp.conf
sudo a2enmod wsgi headers rewrite
sudo a2ensite ihwapp

sudo chown -R root:www-data /var/www/ihwapp
sudo find /var/www/ihwapp -type d -exec chmod 0755 {} \;
sudo find /var/www/ihwapp -type f -exec chmod 0644 {} \;
sudo install -d -o www-data -g www-data -m 0755 /var/www/ihwapp/IHWApp/staticfiles

sudo -u www-data /var/www/ihwapp/venv/bin/python /var/www/ihwapp/IHWApp/manage.py collectstatic --noinput
sudo apache2ctl configtest
sudo systemctl reload apache2
```

Required values in `/etc/ihwapp/ihwapp.env`:

- `DJANGO_SECRET_KEY`
- `DJANGO_ALLOWED_HOSTS`
- `DJANGO_CSRF_TRUSTED_ORIGINS`
- `DJANGO_FORCE_SCRIPT_NAME=/ihwapp`
- `DJANGO_STATIC_ROOT=/var/www/ihwapp/IHWApp/staticfiles`
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`
- `IHW_ARCHIVE_ROOT=/data/working/IHWv2/data/`

The Apache config redirects `/` to `/ihwapp/`, mounts static files at `/ihwapp/static/`, and sends Django traffic through `WSGIScriptAlias /ihwapp ...`. If Apache will terminate TLS, set the `DJANGO_SECURE_SSL_REDIRECT` and `DJANGO_SECURE_HSTS_*` values in the env file to match that setup.
