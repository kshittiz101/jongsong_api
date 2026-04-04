from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import FeatureViewSet, HeroImageViewSet, ServicesViewSet, LocationListCreateAPIView, LocationDetailAPIView

router = DefaultRouter()
router.register(r"features", FeatureViewSet, basename="feature")
router.register(r"services", ServicesViewSet, basename="services")
router.register(r"hero-images", HeroImageViewSet, basename="hero-image")


urlpatterns = [
    path("", include(router.urls)),
    path('locations/', LocationListCreateAPIView.as_view(), name='location-list'),
    path('locations/<int:pk>/',
         LocationDetailAPIView.as_view(), name='location-detail'),
]
