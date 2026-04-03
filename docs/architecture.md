# Architecture

Jongsong API is a **Django monolith** that exposes a versioned **JSON REST API** with **Django REST Framework (DRF)**. Domain code lives in installable apps under `apps/`; cross-cutting API wiring and helpers live in `common/`; the Django project package is `config/` (settings, root URLConf, WSGI/ASGI).

## Layers

| Layer | Role | Typical locations |
|-------|------|-------------------|
| HTTP / routing | Map URLs to views; aggregate app URLConfs | `config/urls.py`, `common/default_routers.py`, `apps/*/urls.py` |
| Views | DRF `APIView`, `ModelViewSet`, OpenAPI metadata | `apps/*/views/` |
| Serializers | Validation and response shaping | `apps/*/serializers/` |
| Models | Persistence | `apps/*/models/` |
| Shared infrastructure | Routers, pagination, exceptions, permissions | `common/` |

## How `/api/v1/` is assembled

The root URL configuration mounts the versioned API and schema:

```python
# config/urls.py (excerpt)
path("api/v1/", include("common.default_routers")),
path("api/v1/auth/token/", include("apps.accounts.token_urls")),
path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
```

`common/default_routers.py` includes each app’s `urls.py` **without an extra prefix**, so their routes appear directly under `/api/v1/`:

```python
# common/default_routers.py
urlpatterns = [
    path("", include("apps.home.urls")),
    path("", include("apps.pharmacy.urls")),
    path("", include("apps.accounts.urls")),
    path("", include("apps.homecare.urls")),
]
```

Together this means:

- **Business APIs** — paths like `/api/v1/features/`, `/api/v1/auth/login/`, etc., depending on each app’s `urls.py`.
- **JWT (SimpleJWT)** — `TokenObtainPairView` and `TokenRefreshView` from `apps/accounts/token_urls.py` at **`/api/v1/auth/token/`** and **`/api/v1/auth/token/refresh/`**.
- **OpenAPI** — schema at **`/api/schema/`**, Swagger UI at **`/api/docs/`** (drf-spectacular).

Default DRF authentication is JWT; registration, login, refresh, and logout flows are implemented in `apps/accounts/` and documented per-app in [Accounts](apps/accounts.md).

## Entry points

| Entry | Settings module | Notes |
|-------|-----------------|-------|
| `manage.py` | `config.settings.development` | Local CLI and `runserver` |
| `config/wsgi.py` | `config.settings.production` | Traditional WSGI servers |
| `config/asgi.py` | `config.settings.production` | ASGI servers |

See [Configuration](configuration.md) for how `DJANGO_SETTINGS_MODULE` and environment variables fit together.
