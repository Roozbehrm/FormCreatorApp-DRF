from django.urls import re_path

from .consumers import FormReportConsumer

websocket_urlpatterns = [
    re_path(r"^ws/reports/forms/(?P<uuid>[0-9a-f-]+)/$", FormReportConsumer.as_asgi()),
]
