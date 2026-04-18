from django.utils import timezone
from rest_framework import serializers

from ..models import PatientCaretakerAssignment


class PatientCaretakerAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientCaretakerAssignment
        fields = [
            "id",
            "patient",
            "caretaker",
            "is_active",
            "assigned_at",
            "ended_at",
            "notes",
            "assigned_by",
        ]
        read_only_fields = ["id", "assigned_at", "assigned_by"]

    def validate(self, attrs):
        if self.instance:
            patient = attrs.get("patient", self.instance.patient)
            caretaker = attrs.get("caretaker", self.instance.caretaker)
            is_active = attrs.get("is_active", self.instance.is_active)
            ended_at = attrs.get("ended_at", self.instance.ended_at)
            notes = attrs.get("notes", self.instance.notes)
        else:
            patient = attrs.get("patient")
            caretaker = attrs.get("caretaker")
            is_active = attrs.get("is_active", True)
            ended_at = attrs.get("ended_at")
            notes = attrs.get("notes", "")

        if patient is None or caretaker is None:
            return attrs

        inst = PatientCaretakerAssignment(
            patient=patient,
            caretaker=caretaker,
            is_active=is_active,
            ended_at=ended_at,
            notes=notes or "",
        )
        if self.instance:
            inst.pk = self.instance.pk
            inst.clean()
        else:
            inst.full_clean()
        return attrs

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data["assigned_by"] = request.user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if validated_data.get("is_active") is False and validated_data.get("ended_at") is None:
            validated_data = {**validated_data, "ended_at": timezone.now()}
        return super().update(instance, validated_data)
