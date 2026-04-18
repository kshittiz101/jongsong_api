from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ReadOnlyModelViewSet
from drf_spectacular.utils import extend_schema

from ..models import HeroImage
from ..serializers import HeroImageSerializer



@extend_schema(tags=["hero images"])
class HeroImageViewSet(ReadOnlyModelViewSet):
    queryset = HeroImage.objects.all()
    serializer_class = HeroImageSerializer
    permission_classes = [AllowAny]
