from rest_framework import serializers

from ..models import Prescription


class PrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prescription
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make status read-only unless user is superuser or pharmacist
        request = self.context.get("request")
        if request:
            user = request.user
            if not self._can_update_status(user):
                self.fields["status"].read_only = True

    def _can_update_status(self, user):
        """Check if user can update prescription status."""
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser:
            return True

        staff_profile = getattr(user, "staff_profile", None)
        if staff_profile is None:
            return False

        designation = getattr(staff_profile, "designation", None)
        if designation is None:
            return False

        return designation.name.lower() == "pharmacist"
