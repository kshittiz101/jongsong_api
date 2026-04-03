from django.urls import include, path

urlpatterns = [
    path("", include("apps.home.urls")),
    path("", include("apps.pharmacy.urls")),
    path("", include("apps.accounts.urls")),
    path("", include("apps.homecare.urls")),
]
