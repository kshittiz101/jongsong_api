# Accounts

## Purpose

Handles **custom users**, **staff/admin/patient profiles**, **registration**, **session-oriented auth views** (login, refresh, logout, current user), and **designation** management. **JWT access/refresh** for API clients is provided via SimpleJWT routes wired separately in `apps/accounts/token_urls.py`.

## URLs

All paths below are served under **`/api/v1/`** because `apps.accounts.urls` is included from `common/default_routers.py`.

| Area | Module | Pattern (after `/api/v1/`) |
|------|--------|----------------------------|
| Designations | `apps/accounts/urls.py` | `admin/designations/`, `admin/designations/<pk>/` |
| Auth & registration | `apps/accounts/urls.py` | `auth/public-user/`, `auth/admin-user/`, `auth/staff-user/`, `auth/login/`, `auth/authenticate-user/`, `auth/refresh/`, `auth/logout/` |
| Legacy aliases | `apps/accounts/urls.py` | `register/`, `admin/register/`, `staff/register/` |
| Patient onboarding | `apps/accounts/urls.py` | `admin/patient-users/` |
| Staff admin API | `apps/accounts/urls.py` (`SimpleRouter`) | `admin/staff/` … |
| Patient profiles (admin) | `apps/accounts/urls.py` (`SimpleRouter`) | `admin/patient-profiles/` … |

**JWT (SimpleJWT)** — `apps/accounts/token_urls.py` is mounted in `config/urls.py` at **`/api/v1/auth/token/`**:

- Token obtain: **`/api/v1/auth/token/`**
- Token refresh: **`/api/v1/auth/token/refresh/`**

## Package layout

| Path | Role |
|------|------|
| `apps.py` | `AccountsConfig` — `name = 'apps.accounts'` |
| `urls.py` | URLConf: paths above + `SimpleRouter` registrations |
| `token_urls.py` | SimpleJWT `TokenObtainPairView`, `TokenRefreshView` |
| `views/` | `auth.py`, `patient.py`, `staff.py` |
| `serializers/` | Auth, patient, staff serializers |
| `models/` | `user.py`, profiles, `designation.py` |
| `permissions/patient.py` | Patient-profile access |
| `backends.py` | Email/phone authentication backend |

Notable: keep **`token_urls.py`** in mind when tracing **JWT** vs app-specific **`auth/`** routes.
