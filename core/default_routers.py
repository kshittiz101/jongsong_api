from django.urls import include, path

urlpatterns = [
    path("", include("home.urls")),
    path("", include("pharmacy.urls")),
    path("", include("accounts.urls")),
    path("", include("staff.urls")),
]
