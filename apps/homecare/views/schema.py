"""Shared drf-spectacular metadata for clinical home-care viewsets."""

from drf_spectacular.utils import extend_schema

HOMECARE_SCHEMA_TAG = ["home care"]
HOMECARE_SCHEMA_ACTIONS = (
    "list",
    "retrieve",
    "create",
    "update",
    "partial_update",
    "destroy",
)

HOMECARE_CLINICAL_SCHEMA = {
    a: extend_schema(tags=HOMECARE_SCHEMA_TAG) for a in HOMECARE_SCHEMA_ACTIONS
}

HOMECARE_ASSIGNMENT_SCHEMA_TAG = ["home care", "caretaker assignments"]
HOMECARE_ASSIGNMENT_SCHEMA = {
    a: extend_schema(tags=HOMECARE_ASSIGNMENT_SCHEMA_TAG)
    for a in HOMECARE_SCHEMA_ACTIONS
}

HOMECARE_DAILY_CLINICAL_SCHEMA = {
    a: extend_schema(tags=HOMECARE_SCHEMA_TAG) for a in ("list", "retrieve")
}
