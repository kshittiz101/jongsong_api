from django.urls import include, path
from rest_framework.routers import DefaultRouter

from home.views import FeatureViewSet, ServicesViewSet

router = DefaultRouter()
router.register(r"features", FeatureViewSet, basename="feature")
router.register(r"services", ServicesViewSet, basename="services")

urlpatterns = [
    path("", include(router.urls)),
]

