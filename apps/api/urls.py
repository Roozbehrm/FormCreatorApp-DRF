from django.urls import include, path

urlpatterns = [
    path("", include("apps.forms.urls")),
]
