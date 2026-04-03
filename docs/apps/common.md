# Common

## Purpose

The **`common`** Django app holds **cross-cutting API infrastructure** shared by domain apps: default **URL aggregation** for `/api/v1/`, **pagination**, **exception handling**, **permissions**, **parsers**, **mixins**, and **constants**. It is **not** a separate HTTP “surface” with its own public prefix beyond what `common/default_routers.py` wires.

## URLs

There is **no** `urls.py` with view routes in `common/`. Instead, **`common/default_routers.py`** is included from `config/urls.py` at **`/api/v1/`** and re-exports each app’s `urlpatterns`:

```text
apps.home.urls
apps.pharmacy.urls
apps.accounts.urls
apps.homecare.urls
```

See [Architecture](../architecture.md) for the full picture.

## Package layout

| Path | Role |
|------|------|
| `apps.py` | `CommonConfig` — `name = 'common'` |
| `default_routers.py` | Aggregates app URLConfs under `/api/v1/` |
| `pagination.py` | DRF pagination (e.g. standard results envelope) |
| `exceptions.py` | Custom DRF exception handler |
| `permissions.py` | Shared permission classes |
| `parsers.py` | Custom parsers if any |
| `mixins.py` | Shared view mixins |
| `constants/` | Role, gender, blood group, patient type constants |
| `image_validators.py` | Upload validation helpers |
| `models.py`, `views.py`, `admin.py` | Placeholders / minimal project glue |
