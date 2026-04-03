# Pharmacy

## Purpose

**Pharmacy catalog** API: **suppliers**, **categories**, and **medicines** exposed as DRF viewsets.

## URLs

Mounted under **`/api/v1/`**. Router: **`DefaultRouter`** in `apps/pharmacy/urls.py`.

| Registered route | ViewSet | basename |
|------------------|---------|----------|
| `suppliers/` | `SupplierViewSet` | `supplier` |
| `categories/` | `CategoryViewSet` | `category` |
| `medicines/` | `MedicineViewSet` | `medicine` |

## Package layout

| Path | Role |
|------|------|
| `apps.py` | `PharmacyConfig` — `name = 'apps.pharmacy'` |
| `urls.py` | `DefaultRouter` + `include(router.urls)` |
| `views/` | `supplier.py`, `category.py`, `medicine.py` |
| `serializers/` | Matching serializers |
| `models/` | `supplier.py`, `category.py`, `medicine.py` |
| `admin.py` | Django admin for catalog entities |
| `fixtures/` | Optional dummy data for local use |
