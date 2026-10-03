from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.forms.views import (
    FieldViewSet,
    FormUnlockView,
    FormViewSet,
    PublicFormSubmitView,
    PublicFormView,
    PublicSubmissionAnswerView,
    PublicSubmissionFinalizeView,
    PublicSubmissionStartView,
)

app_name = "forms"

router = DefaultRouter()
router.register("forms", FormViewSet, basename="form")

urlpatterns = [
    path("", include(router.urls)),
    path("public/forms/<uuid:uuid>/", PublicFormView.as_view(), name="public-form"),
    path("public/forms/<uuid:uuid>/unlock/", FormUnlockView.as_view(), name="form-unlock"),
    path("public/forms/<uuid:uuid>/submit/", PublicFormSubmitView.as_view(), name="public-form-submit"),
    path("public/forms/<uuid:uuid>/start/", PublicSubmissionStartView.as_view(), name="public-submission-start"),
    path(
        "public/forms/<uuid:uuid>/submissions/<int:submission_id>/answer/<int:field_id>/",
        PublicSubmissionAnswerView.as_view(),
        name="public-submission-answer",
    ),
    path(
        "public/forms/<uuid:uuid>/submissions/<int:submission_id>/finalize/",
        PublicSubmissionFinalizeView.as_view(),
        name="public-submission-finalize",
    ),
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
