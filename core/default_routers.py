from django.urls import include, path

urlpatterns = [
    path("", include("pharmacy.urls")),
    path("", include("accounts.urls")),
]
