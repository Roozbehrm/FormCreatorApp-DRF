from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter

from .views import (
    ProcessStepViewSet,
    ProcessUnlockView,
    ProcessViewSet,
    PublicProcessStateView,
    PublicProcessStepSubmitView,
    PublicProcessView,
)
app_name = "processes"

router = DefaultRouter()
router.register("processes", ProcessViewSet, basename="process")

steps_router = NestedDefaultRouter(router, "processes", lookup="process")
steps_router.register("steps", ProcessStepViewSet, basename="process-steps")

urlpatterns = [
    path("", include(router.urls)),
    path("", include(steps_router.urls)),
    path("public/processes/<uuid:uuid>/", PublicProcessView.as_view(), name="public-process"),
    path("public/processes/<uuid:uuid>/unlock/", ProcessUnlockView.as_view(), name="process-unlock"),
    path("public/processes/<uuid:uuid>/state/", PublicProcessStateView.as_view(), name="process-state"),
    path(
        "public/processes/<uuid:uuid>/steps/<int:step_id>/submit/",
        PublicProcessStepSubmitView.as_view(),
        name="process-step-submit",
    ),
]
