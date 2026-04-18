"""
Build or refresh `PatientDailyClinicalReport` from source rows.

Day boundaries are [local midnight, next midnight) in `settings.TIME_ZONE`.
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta
from decimal import Decimal
from typing import Any
from zoneinfo import ZoneInfo

from django.conf import settings
from django.db.models.functions import Coalesce

from ..models import Medication, MedicationLog, PatientDailyClinicalReport, PatientVitalReading


def _local_day_bounds(report_date: date) -> tuple[datetime, datetime]:
    tz = ZoneInfo(str(settings.TIME_ZONE))
    start = datetime.combine(report_date, time.min, tzinfo=tz)
    end = start + timedelta(days=1)
    return start, end


def _json_safe(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def build_or_refresh_report(patient_user, report_date: date) -> PatientDailyClinicalReport:
    start, end = _local_day_bounds(report_date)

    log_qs = (
        MedicationLog.objects.filter(medication__patient_id=patient_user.pk)
        .select_related("medication", "marked_by")
        .annotate(ref_time=Coalesce("scheduled_time", "actual_taken_time"))
        .filter(ref_time__gte=start, ref_time__lt=end)
        .order_by("ref_time", "id")
    )

    log_entries: list[dict[str, Any]] = []
    med_ids_with_logs: set[int] = set()
    for log in log_qs:
        med = log.medication
        if med:
            med_ids_with_logs.add(med.pk)
        log_entries.append(
            {
                "log_id": log.pk,
                "medication_id": med.pk if med else None,
                "medication_name": med.medication_name if med else None,
                "dosage": med.dosage if med else None,
                "scheduled_time": _json_safe(log.scheduled_time) if log.scheduled_time else None,
                "actual_taken_time": _json_safe(log.actual_taken_time) if log.actual_taken_time else None,
                "status": log.status,
                "notes": log.notes or "",
                "marked_by_id": log.marked_by_id,
            }
        )

    active_meds = Medication.objects.filter(
        patient_id=patient_user.pk,
        is_active=True,
    ).order_by("medication_name", "id")

    meds_without_logs: list[dict[str, Any]] = []
    for med in active_meds:
        if med.pk not in med_ids_with_logs:
            meds_without_logs.append(
                {
                    "medication_id": med.pk,
                    "medication_name": med.medication_name,
                    "dosage": med.dosage,
                    "frequency": med.frequency,
                    "times": med.times,
                }
            )

    med_lines: list[str] = []
    for row in log_entries:
        name = row.get("medication_name") or "Medication"
        st = row.get("scheduled_time") or row.get("actual_taken_time") or "—"
        med_lines.append(f"{name} ({row.get('status')}) @ {st}")
    if meds_without_logs:
        med_lines.append("— Active medications with no dose logs this day —")
        for m in meds_without_logs:
            nm = m.get("medication_name") or "Medication"
            med_lines.append(f"{nm}: no doses recorded")

    medication_summary: dict[str, Any] = {
        "logs": log_entries,
        "medications_without_logs_today": meds_without_logs,
    }
    medication_summary_text = "\n".join(med_lines) if med_lines else "No medication logs for this day."

    vitals_qs = (
        PatientVitalReading.objects.filter(
            patient_id=patient_user.pk,
            recorded_at__gte=start,
            recorded_at__lt=end,
        )
        .select_related("recorded_by")
        .order_by("recorded_at", "id")
    )

    readings: list[dict[str, Any]] = []
    hr_vals: list[int] = []
    sys_vals: list[int] = []
    dia_vals: list[int] = []
    spo2_vals: list[int] = []
    last_hr = last_sys = last_dia = last_spo2 = None

    for v in vitals_qs:
        readings.append(
            {
                "id": v.pk,
                "recorded_at": v.recorded_at.isoformat(),
                "systolic_mmhg": v.systolic_mmhg,
                "diastolic_mmhg": v.diastolic_mmhg,
                "heart_rate_bpm": v.heart_rate_bpm,
                "temperature_celsius": _json_safe(v.temperature_celsius) if v.temperature_celsius is not None else None,
                "spo2_percent": v.spo2_percent,
                "respiratory_rate": v.respiratory_rate,
                "blood_glucose_mg_dl": v.blood_glucose_mg_dl,
                "weight_kg": _json_safe(v.weight_kg) if v.weight_kg is not None else None,
                "height_cm": v.height_cm,
                "notes": v.notes or "",
            }
        )
        if v.heart_rate_bpm is not None:
            hr_vals.append(v.heart_rate_bpm)
            last_hr = v.heart_rate_bpm
        if v.systolic_mmhg is not None:
            sys_vals.append(v.systolic_mmhg)
            last_sys = v.systolic_mmhg
        if v.diastolic_mmhg is not None:
            dia_vals.append(v.diastolic_mmhg)
            last_dia = v.diastolic_mmhg
        if v.spo2_percent is not None:
            spo2_vals.append(v.spo2_percent)
            last_spo2 = v.spo2_percent

    def _stat(vals: list[int], last):
        if not vals:
            return None
        return {"min": min(vals), "max": max(vals), "last": last}

    vitals_summary: dict[str, Any] = {
        "readings": readings,
        "stats": {
            "heart_rate_bpm": _stat(hr_vals, last_hr),
            "blood_pressure_mmhg": (
                {
                    "systolic": _stat(sys_vals, last_sys),
                    "diastolic": _stat(dia_vals, last_dia),
                }
                if (sys_vals or dia_vals)
                else None
            ),
            "spo2_percent": _stat(spo2_vals, last_spo2),
        },
    }

    vital_lines: list[str] = []
    if readings:
        vital_lines.append(f"{len(readings)} reading(s).")
        if vitals_summary["stats"]["heart_rate_bpm"]:
            s = vitals_summary["stats"]["heart_rate_bpm"]
            vital_lines.append(f"Heart rate bpm: min {s['min']}, max {s['max']}, last {s['last']}.")
        bp = vitals_summary["stats"].get("blood_pressure_mmhg") or {}
        if bp.get("systolic") and bp.get("diastolic"):
            vital_lines.append(
                f"BP mmHg (last): {bp['systolic']['last']}/{bp['diastolic']['last']}."
            )
        if vitals_summary["stats"]["spo2_percent"]:
            s = vitals_summary["stats"]["spo2_percent"]
            vital_lines.append(f"SpO₂ %: min {s['min']}, max {s['max']}, last {s['last']}.")
    else:
        vital_lines.append("No vitals recorded for this day.")

    vitals_summary_text = "\n".join(vital_lines)

    row, _ = PatientDailyClinicalReport.objects.update_or_create(
        patient=patient_user,
        report_date=report_date,
        defaults={
            "medication_summary": medication_summary,
            "medication_summary_text": medication_summary_text,
            "vitals_summary": vitals_summary,
            "vitals_summary_text": vitals_summary_text,
        },
    )
    return row
