# Configuration

Settings are split under `config/settings/`: shared defaults in **`base.py`**, local development overrides in **`development.py`**, and production overrides in **`production.py`**. A shim at `config/settings.py` re-exports development for tools that import `config.settings` directly.

## Django settings module

| Context | Typical `DJANGO_SETTINGS_MODULE` |
|---------|----------------------------------|
| Local development (`manage.py`) | `config.settings.development` |
| Production WSGI/ASGI | `config.settings.production` |

`development.py` and `production.py` both start with `from .base import *` and then override `DEBUG`, database, email, logging, and security flags as needed.

## Environment variables (names only)

Values are loaded with **python-decouple** (`config()`) in `config/settings/base.py` and `production.py`. Set these in `.env` or the process environment (never commit secrets).

### Core and HTTP

- `SECRET_KEY`
- `DEBUG`
- `ALLOWED_HOSTS`

### OpenAPI / Spectacular (optional overrides)

- `SPECTACULAR_TITLE`
- `SPECTACULAR_DESCRIPTION`
- `SPECTACULAR_VERSION`
- `SPECTACULAR_SERVE_INCLUDE_SCHEMA`

### Email (base defaults; production may use SMTP)

- `EMAIL_HOST`
- `EMAIL_PORT`
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`
- `EMAIL_USE_TLS`
- `EMAIL_USE_SSL`
- `EMAIL_TIMEOUT`
- `DEFAULT_FROM_EMAIL`
- `SERVER_EMAIL`

### Production database (`config/settings/production.py`)

- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST` (optional, default in code)
- `DB_PORT` (optional, default in code)

### Production email backend

- `EMAIL_BACKEND` (optional; defaults to SMTP backend in code)

Development uses SQLite (`development.py`) and console email; production uses PostgreSQL and stricter cookie/HTTPS settings. Adjust `INSTALLED_APPS`, `REST_FRAMEWORK`, `SIMPLE_JWT`, and `SPECTACULAR_SETTINGS` in `config/settings/base.py` when changing global API behavior.
