from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ReadOnlyModelViewSet

from ..models import Services
from ..serializers import ServicesSerializer
from drf_spectacular.utils import extend_schema

@extend_schema(tags=["services"])
class ServicesViewSet(ReadOnlyModelViewSet):
    queryset = Services.objects.all()
    serializer_class = ServicesSerializer
    permission_classes = [AllowAny]
