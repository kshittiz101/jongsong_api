from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import AllowAny
from home.models import Feature, Services
from home.serializers import FeatureSerializer, ServicesSerializer


class FeatureViewSet(ReadOnlyModelViewSet):
    queryset = Feature.objects.all()
    serializer_class = FeatureSerializer
    permission_classes = [AllowAny]


class ServicesViewSet(ReadOnlyModelViewSet):
    queryset = Services.objects.all()
    serializer_class = ServicesSerializer
    permission_classes = [AllowAny]
