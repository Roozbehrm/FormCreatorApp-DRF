from django.urls import include, path

urlpatterns = [
    path("auth/", include("apps.accounts.urls")),
    path("", include("apps.categories.urls")),
    path("", include("apps.forms.urls")),
    path("", include("apps.processes.urls")),
    path("", include("apps.reports.urls")),
]
