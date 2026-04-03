# Home

## Purpose

Read/write API for **marketing-style content**: **features**, **services**, and **hero images** used by storefront or landing experiences.

## URLs

Mounted under **`/api/v1/`** via `common/default_routers.py`. Router: **`DefaultRouter`** in `apps/home/urls.py`.

| Registered route | ViewSet | Notes |
|------------------|---------|--------|
| `features/` | `FeatureViewSet` | basename `feature` |
| `services/` | `ServicesViewSet` | basename `services` |
| `hero-images/` | `HeroImageViewSet` | basename `hero-image` |

## Package layout

| Path | Role |
|------|------|
| `apps.py` | `HomeConfig` — `name = 'apps.home'` |
| `urls.py` | `DefaultRouter` registrations |
| `views/` | `feature.py`, `services.py`, `hero_image.py` |
| `serializers/` | Matching serializers per resource |
| `models/` | `feature.py`, `services.py`, `hero_image.py` |
| `admin.py` | Django admin registration |
| `fixtures/` | Sample JSON fixtures (optional local seeding) |
