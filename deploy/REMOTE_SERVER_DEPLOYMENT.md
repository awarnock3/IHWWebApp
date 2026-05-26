# Remote Server Deployment for Ubuntu 24.04

This guide consolidates the current local deployment notes from `README.md`, `.env.example`, `deploy/apache/install_ihwapp.sh`, `deploy/apache/ihwapp.conf`, and `IHWApp/IHWApp/settings.py` into a remote-server migration procedure for an Ubuntu 24.04 host with Apache already installed.

## What this deployment assumes

- MariaDB is already present on the remote host, with the same schema and credentials used by this app.
- Apache is already installed and running.
- You want to keep the existing `/ihwapp` URL prefix used by the current Apache and Django configuration.
- You are **not** creating or migrating database tables from Django. This project uses a legacy schema and the models are read-only representations of that database.

## What must exist on the remote host

### System packages

Install the OS packages needed for Django, Apache `mod_wsgi`, and the `mysqlclient` Python package:

```bash
sudo apt update
sudo apt install -y \
  build-essential \
  default-libmysqlclient-dev \
  libapache2-mod-wsgi-py3 \
  pkg-config \
  python3-dev \
  python3-venv \
  rsync
```

### Python packages

Install these into the remote virtual environment from `requirements.txt`:

- `Django==6.0.4`
- `asgiref==3.11.1`
- `mysqlclient==2.2.8`
- `sqlparse==0.5.5`

### Application data outside the repository

The web application reads archive files directly from the filesystem through `IHW_ARCHIVE_ROOT`. The default path used here is:

```bash
/data/working/IHWv2/data/
```

That archive tree is **not** bundled into the upload tarball. If the remote server should support FITS header viewing, PDS label viewing, and file/document browsing, copy or mount the archive files onto the remote host and point `IHW_ARCHIVE_ROOT` at that location.

## Files included in the upload bundle

The tarball built for this deployment contains the application source and deployment assets needed on the remote host:

- `IHWApp/` Django project and apps
- `deploy/` Apache config, installer script, and this deployment guide
- `.env.example`
- `requirements.txt`
- `README.md`
- supporting repository files referenced by the deployment docs

The bundle intentionally excludes:

- `.git/`
- local `venv/`
- `__pycache__/`
- generated `IHWApp/staticfiles/`

## Recommended target layout

Deploy to:

```bash
/var/www/ihwapp/
├── IHWApp/
│   ├── manage.py
│   ├── IHWApp/
│   ├── core/
│   └── search/
├── deploy/
├── requirements.txt
└── venv/
```

Runtime settings are read from:

```bash
/etc/ihwapp/ihwapp.env
```

## Remote deployment steps

### 1. Upload the tarball

Copy the generated tarball from this workstation to the remote host, for example:

```bash
scp ihwapp-remote-server-bundle-20260521.tar.gz user@remote-host:/tmp/
```

### 2. Extract the application under `/var/www/ihwapp`

```bash
sudo mkdir -p /var/www/ihwapp
sudo tar -xzf /tmp/ihwapp-remote-server-bundle-20260521.tar.gz \
  -C /var/www/ihwapp \
  --strip-components=1
```

### 3. Create the virtual environment and install Python dependencies

```bash
sudo python3 -m venv /var/www/ihwapp/venv
sudo /var/www/ihwapp/venv/bin/pip install --upgrade pip
sudo /var/www/ihwapp/venv/bin/pip install -r /var/www/ihwapp/requirements.txt
```

### 4. Create the runtime environment file

```bash
sudo install -d -o root -g www-data -m 0750 /etc/ihwapp
sudo install -o root -g www-data -m 0640 /var/www/ihwapp/.env.example /etc/ihwapp/ihwapp.env
sudo editor /etc/ihwapp/ihwapp.env
```

Set these values explicitly:

```dotenv
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=<generate-a-new-random-secret>
DJANGO_ALLOWED_HOSTS=<public-hostname>,<optional-secondary-hostname>,<optional-public-ip>
DJANGO_CSRF_TRUSTED_ORIGINS=https://<public-hostname>,https://<optional-secondary-hostname>
DJANGO_FORCE_SCRIPT_NAME=/ihwapp
DJANGO_STATIC_ROOT=/var/www/ihwapp/IHWApp/staticfiles
DJANGO_SECURE_COOKIES=True
DJANGO_SECURE_SSL_REDIRECT=True
DJANGO_SECURE_HSTS_SECONDS=31536000
DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS=False
DJANGO_SECURE_HSTS_PRELOAD=False
DJANGO_SECURE_REFERRER_POLICY=same-origin

DB_NAME=ihwdb2
DB_USER=ihwuser
DB_PASSWORD=<existing-db-password>
DB_HOST=localhost
DB_PORT=3306

IHW_ARCHIVE_ROOT=/data/working/IHWv2/data/
```

Notes:

- Keep `DJANGO_FORCE_SCRIPT_NAME=/ihwapp` unless you are also changing the Apache aliases.
- `DJANGO_ALLOWED_HOSTS` must contain only hostnames or IPs, comma-separated. Do **not** include `https://`, ports, or `/ihwapp`. Example: `DJANGO_ALLOWED_HOSTS=ihw.example.org,www.ihw.example.org`.
- `DJANGO_CSRF_TRUSTED_ORIGINS` must contain full origins including scheme. Example: `DJANGO_CSRF_TRUSTED_ORIGINS=https://ihw.example.org,https://www.ihw.example.org`.
- For a public HTTPS deployment behind Apache TLS termination, keep `DJANGO_SECURE_SSL_REDIRECT=True` and set the `DJANGO_SECURE_HSTS_*` values to match your site policy.

### 5. Make sure the archive data path exists

This step is optional. The application can run without the archive mounted; in that mode it will continue to serve database-backed search results and suppress file-backed viewing links where `archive_available` is false.

If the remote server does not already have the archive tree and you want file-backed views later, copy it from the source machine or mount it from shared storage. Run the example below from the **source machine**, not from the remote host:

```bash
sudo rsync -a /data/working/IHWv2/data/ remote-host:/data/working/IHWv2/data/
```

If you place the archive elsewhere, update `IHW_ARCHIVE_ROOT` in `/etc/ihwapp/ihwapp.env`.

If you are deploying **without** the archive for now, either:

- leave `IHW_ARCHIVE_ROOT` set to the future mount point and do not create that directory yet, or
- set it to another path that does not currently exist

In both cases, `is_archive_available()` will remain false and the UI will show metadata without offering file-backed access.

### 6. Review and install the Apache site configuration

Edit the bundled Apache config before enabling it:

```bash
sudo editor /var/www/ihwapp/deploy/apache/ihwapp.conf
```

Update at least:

- `ServerName` to the remote hostname
- `ServerAdmin` to the appropriate contact address

Then install and enable the site:

```bash
sudo install -m 0644 /var/www/ihwapp/deploy/apache/ihwapp.conf /etc/apache2/sites-available/ihwapp.conf
sudo a2enmod wsgi headers rewrite
sudo a2ensite ihwapp
```

### 6a. Configure the HTTPS `*:443` vhost

The bundled `deploy/apache/ihwapp.conf` file covers the initial HTTP `*:80` site only. If the site will be public over HTTPS, Apache must also have a matching SSL vhost for the same hostname.

In the current deployment pattern, Let's Encrypt `certbot` writes that SSL vhost to:

```bash
/etc/apache2/sites-enabled/ihwapp-le-ssl.conf
```

That `*:443` vhost must include the same application routing directives as the HTTP vhost:

- `RedirectMatch 302 ^/$ /ihwapp/`
- `Alias /ihwapp/static/ /var/www/ihwapp/IHWApp/staticfiles/`
- the `<Directory ...>` blocks for static files and `wsgi.py`
- `WSGIDaemonProcess ihwapp ...`
- `WSGIProcessGroup ihwapp`
- `WSGIScriptAlias /ihwapp /var/www/ihwapp/IHWApp/IHWApp/wsgi.py`

It must also contain the certificate paths installed by `certbot`, typically in the same `ihwapp-le-ssl.conf` file.

This matters because HTTPS requests are handled by the `*:443` vhost, not the `*:80` vhost. If the SSL vhost is missing the alias and WSGI directives, Apache may show a directory listing at `https://<host>/` or return a 404 at `https://<host>/ihwapp` even though the HTTP vhost looks correct.

### 7. Set ownership and collect static files

```bash
sudo chown -R root:www-data /var/www/ihwapp
sudo find /var/www/ihwapp -type d -exec chmod 0755 {} \;
sudo find /var/www/ihwapp -type f -exec chmod 0644 {} \;
sudo chmod 0755 /var/www/ihwapp/IHWApp/manage.py
sudo install -d -o www-data -g www-data -m 0755 /var/www/ihwapp/IHWApp/staticfiles

sudo -u www-data /var/www/ihwapp/venv/bin/python /var/www/ihwapp/IHWApp/manage.py collectstatic --noinput
```

### 8. Validate Django and Apache, then reload Apache

```bash
sudo -u www-data /var/www/ihwapp/venv/bin/python /var/www/ihwapp/IHWApp/manage.py check
sudo apache2ctl configtest
sudo systemctl reload apache2
```

## Post-deployment checks

Verify:

1. `https://<public-hostname>/ihwapp/` loads through the SSL vhost.
2. Static assets load under `https://<public-hostname>/ihwapp/static/`.
3. Search pages connect to MariaDB successfully.
4. If the archive is not mounted yet, observation detail pages should show the warning that archive files are unavailable instead of offering file-backed access.
5. File-backed views work once archive data is copied and `IHW_ARCHIVE_ROOT` is correct.

## One-command installer option

After extraction, you can also run the bundled installer:

```bash
cd /var/www/ihwapp
sudo ./deploy/apache/install_ihwapp.sh
```

Use that only after reviewing:

- `/var/www/ihwapp/deploy/apache/ihwapp.conf`
- `/etc/ihwapp/ihwapp.env`

The script now installs the required Ubuntu packages for `mod_wsgi`, virtual environments, `rsync`, and `mysqlclient` build support before setting up the site.

## Important project-specific notes

- Do **not** run `python manage.py migrate` against this database.
- The database is a legacy MariaDB schema; Django models are configured against it rather than managing it.
- The app reads runtime configuration from `/etc/ihwapp/ihwapp.env` automatically through `IHWApp/settings.py`.
- The current Apache deployment serves the app under `/ihwapp`, not at the domain root.
- For HTTPS, the live SSL vhost may be maintained by `certbot` in `/etc/apache2/sites-enabled/ihwapp-le-ssl.conf`; keep its alias and WSGI routing in sync with the HTTP site config.
