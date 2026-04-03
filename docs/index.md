# Jongsong API

Wiki-style documentation for the **Jongsong** Django REST API: pharmacy catalog, home-care coordination, JWT auth, and OpenAPI.

- **[Architecture](architecture.md)** — how apps, URLs, and DRF fit together
- **[Configuration](configuration.md)** — settings modules and environment variables

When the development server is running, interactive API docs are at [`/api/docs/`](http://127.0.0.1:8000/api/docs/) (Swagger UI).

## App reference

- [Accounts](apps/accounts.md) — users, profiles, auth, JWT-adjacent routes
- [Home](apps/home.md) — features, services, hero content
- [Home care](apps/homecare.md) — vitals, medications, care assignments
- [Pharmacy](apps/pharmacy.md) — suppliers, categories, medicines
- [Common](apps/common.md) — shared routers, pagination, DRF helpers
