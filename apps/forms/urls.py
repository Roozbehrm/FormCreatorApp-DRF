from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.forms.views import FieldViewSet, FormViewSet

app_name = "forms"

router = DefaultRouter()
router.register("forms", FormViewSet, basename="form")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "forms/<uuid:form_uuid>/fields/",
        FieldViewSet.as_view({"get": "list", "post": "create"}),
        name="field-list",
    ),
    # Bulk reorder
    path(
        "forms/<uuid:form_uuid>/fields/bulk-reorder/",
        FieldViewSet.as_view(
            {
                "patch": "bulk_reorder",
            }
        ),
        name="field-bulk-reorder",
    ),
    path(
        "forms/<uuid:form_uuid>/fields/<int:pk>/",
        FieldViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="field-detail",
    ),
]
