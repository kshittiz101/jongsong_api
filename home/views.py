from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import AllowAny
from home.models import Feature, HeroImage, Services
from home.serializers import FeatureSerializer, HeroImageSerializer, ServicesSerializer


class FeatureViewSet(ReadOnlyModelViewSet):
    queryset = Feature.objects.all()
    serializer_class = FeatureSerializer
    permission_classes = [AllowAny]


class ServicesViewSet(ReadOnlyModelViewSet):
    queryset = Services.objects.all()
    serializer_class = ServicesSerializer
    permission_classes = [AllowAny]


class HeroImageViewSet(ReadOnlyModelViewSet):
    queryset = HeroImage.objects.all()
    serializer_class = HeroImageSerializer
    permission_classes = [AllowAny]
