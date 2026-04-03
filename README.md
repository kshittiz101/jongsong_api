# Jongsong API

Backend API for **Jongsong**, a digital health platform that combines **online pharmacy** (catalog, orders, delivery) with **home-care coordination** (patients, staff assignments, care workflows). This repository exposes a **REST API** consumed by web and mobile clients, with **JWT authentication**, **role-aware access**, and **OpenAPI documentation**.

---

## Tech stack

| Layer | Technology |
|--------|------------|
| Language | Python **3.10** |
| Dependencies | **Pipenv** (`Pipfile` / `Pipfile.lock`) |
| Framework | **Django 5.2** |
| API | **Django REST Framework** |
| Auth | **djangorestframework-simplejwt** (access/refresh, token blacklist) |
| API schema & docs | **drf-spectacular** (OpenAPI 3, Swagger UI) |
| Configuration | **python-decouple** (environment / `.env`) |
| Images | **Pillow** (`ImageField`, upload validation) |
| Default database | **SQLite** (`db.sqlite3`) — replace for production |
| Tests | **pytest** + **pytest-django** |
| Formatting / lint | **Black**, **Flake8** |

---

## Project layout

| Path | Purpose |
|------|---------|
| `config/` | Django project (`settings.py`, `urls.py`, WSGI) |
| `core/` | Shared routers, constants, validators |
| `accounts/` | Custom user model, email/phone auth backend |
| `home/` | Storefront-style content (e.g. hero, features) |
| `pharmacy/` | Pharmacy catalog and related APIs |
| `staff/` | Staff profiles and operations |
| `patient/` | Patient profiles, medications, home-care context |
| `normal_user/` | Normal-user app integration |

API routes are mounted under **`/api/`** (see `config/urls.py` and `core/default_routers.py`).

---

## Prerequisites

- **Python 3.10** (the `Pipfile` pins `python_full_version = 3.10.14`; use 3.10.x)
- **[Pipenv](https://pipenv.pypa.io/)** for installing dependencies and running commands

---

## Setup

### 1. Clone and enter the project

```bash
git clone <repository-url>
cd jongsong_api
```

### 2. Install dependencies

Install application and development dependencies:

```bash
pipenv install --dev
```

Production-only install (no dev tools):

```bash
pipenv install
```

### 3. Environment variables

Copy the example env file and adjust values:

```bash
cp .env.example .env
```

**Required** for `config/settings.py` (in addition to the variables in `.env.example`):

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Django secret key (use a strong value in production) |
| `DEBUG` | `True` for local dev; `False` in production |
| `ALLOWED_HOSTS` | Comma-separated hosts, e.g. `localhost,127.0.0.1` |
| `SPECTACULAR_TITLE` | API title shown in OpenAPI / Swagger |
| `SPECTACULAR_DESCRIPTION` | Short API description |
| `SPECTACULAR_VERSION` | API version string (e.g. `1.0.0`) |

Optional: `SPECTACULAR_SERVE_INCLUDE_SCHEMA` (boolean), and email/SMTP variables when `DEBUG=False` — see comments in `.env.example`.

### 4. Database migrations

```bash
pipenv run python manage.py migrate
```

### 5. Create a superuser (optional, for Django admin)

```bash
pipenv run python manage.py createsuperuser
```

### 6. Run the development server

```bash
pipenv run python manage.py runserver
```

The API is available at **`http://127.0.0.1:8000/api/`**.

---

## Useful URLs

| URL | Description |
|-----|-------------|
| `/api/docs/` | **Swagger UI** (interactive API docs) |
| `/api/schema/` | OpenAPI schema |
| `/api/token/` | Obtain JWT pair (POST) |
| `/api/token/refresh/` | Refresh JWT |
| `/django-admin/` | Django admin |

With `DEBUG=True`, user-uploaded media is served at **`/media/`**.

---

## Development commands

```bash
# Run tests
pipenv run pytest

# Format code
pipenv run black .

# Lint
pipenv run flake8
```

---

## Documentation

This repository includes a **MkDocs** site (Material theme) under `docs/` for architecture, configuration, and per-app API layout.

```bash
# Local preview (opens a dev server; default http://127.0.0.1:8000/ for MkDocs)
pipenv run mkdocs serve

# Static build output in site/ (already listed in .gitignore — do not commit)
pipenv run mkdocs build
```

---

## Production notes

- Switch **`DATABASES`** in `config/settings.py` to a production-grade database (e.g. PostgreSQL) and add the appropriate driver.
- Set **`DEBUG=False`**, restrict **`ALLOWED_HOSTS`**, and use a secure **`SECRET_KEY`**.
- Align **`SIMPLE_JWT`** lifetimes and blacklist behavior with your security policy.
- Serve **static** and **media** files with your reverse proxy or object storage as appropriate; do not rely on Django’s dev server.

---

## Further reading

Internal product and stack notes live under **`.projects/`** (requirements, design, implementation notes).
