# Home care

## Purpose

**Home-care clinical and operational** data: **vitals**, **medications**, **dose logs**, **medication reports**, and **care-team assignments**, with strong authorization and **selector-based** query scoping.

## URLs

Mounted under **`/api/v1/`**. Router: **`SimpleRouter`** in `apps/homecare/urls.py`.

| Registered prefix | ViewSet |
|-------------------|---------|
| `admin/home-care/vitals/` | `PatientVitalReadingViewSet` |
| `admin/home-care/medications/` | `HomeCareMedicationViewSet` |
| `admin/home-care/medication-logs/` | `MedicationLogViewSet` |
| `admin/home-care/medication-reports/` | `MedicationReportViewSet` |
| `admin/home-care/care-assignments/` | `PatientCareAssignmentViewSet` |

## Package layout

| Path | Role |
|------|------|
| `apps.py` | `HomecareConfig` — `name = 'apps.homecare'` |
| `urls.py` | `SimpleRouter` registrations |
| `views/` | `vitals.py`, `medication.py`, `report.py`, `care_assignment.py` |
| `serializers/` | Matching serializers |
| `models/` | Domain models per resource |
| `selectors.py` | Centralized `QuerySet` construction and filtering |
| `access.py` | Visibility helpers (e.g. which patients a user may see) |
| `permissions.py` | DRF permission classes for home-care routes |
| `services.py` | Domain services where used |

Notable: **`selectors.py`** is the primary place for reusable list/filter logic consumed from viewsets.
