#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DEPLOY_ROOT="/var/www/ihwapp"
APP_ROOT="$DEPLOY_ROOT/IHWApp"
VENV_ROOT="$DEPLOY_ROOT/venv"
APACHE_SITE_SRC="$REPO_ROOT/deploy/apache/ihwapp.conf"
APACHE_SITE_DEST="/etc/apache2/sites-available/ihwapp.conf"
ENV_DIR="/etc/ihwapp"
ENV_FILE="$ENV_DIR/ihwapp.env"
ENV_EXAMPLE_SRC="$REPO_ROOT/.env.example"

if [[ "${EUID}" -eq 0 ]]; then
    SUDO=()
else
    SUDO=(sudo)
fi

"${SUDO[@]}" apt-get update
"${SUDO[@]}" apt-get install -y libapache2-mod-wsgi-py3

"${SUDO[@]}" install -d "$DEPLOY_ROOT"
"${SUDO[@]}" rsync -a --delete \
    --exclude '.git/' \
    --exclude 'venv/' \
    --exclude '__pycache__/' \
    --exclude 'IHWApp/staticfiles/' \
    "$REPO_ROOT/" "$DEPLOY_ROOT/"

if [[ "${EUID}" -eq 0 ]]; then
    test -d "$DEPLOY_ROOT"
else
    sudo test -d "$DEPLOY_ROOT"
fi

if [[ ! -d "$VENV_ROOT" ]]; then
    "${SUDO[@]}" python3 -m venv "$VENV_ROOT"
fi

"${SUDO[@]}" "$VENV_ROOT/bin/pip" install --upgrade pip
"${SUDO[@]}" "$VENV_ROOT/bin/pip" install -r "$DEPLOY_ROOT/requirements.txt"

"${SUDO[@]}" install -d -m 0750 "$ENV_DIR"
if [[ ! -f "$ENV_FILE" ]]; then
    "${SUDO[@]}" install -m 0640 "$ENV_EXAMPLE_SRC" "$ENV_FILE"
fi

"${SUDO[@]}" install -m 0644 "$APACHE_SITE_SRC" "$APACHE_SITE_DEST"
"${SUDO[@]}" a2enmod wsgi headers rewrite
"${SUDO[@]}" a2ensite ihwapp

"${SUDO[@]}" chown -R root:www-data "$DEPLOY_ROOT"
"${SUDO[@]}" find "$DEPLOY_ROOT" -type d -exec chmod 0755 {} \;
"${SUDO[@]}" find "$DEPLOY_ROOT" -type f -exec chmod 0644 {} \;
"${SUDO[@]}" chmod 0755 "$APP_ROOT/manage.py"
"${SUDO[@]}" install -d -o www-data -g www-data -m 0755 "$APP_ROOT/staticfiles"

"${SUDO[@]}" -u www-data "$VENV_ROOT/bin/python" "$APP_ROOT/manage.py" collectstatic --noinput

"${SUDO[@]}" apache2ctl configtest
"${SUDO[@]}" systemctl reload apache2
