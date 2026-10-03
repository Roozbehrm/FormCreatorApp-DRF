"""
مالک: روزبه (امتیازی)
TODO: websocket_urlpatterns را با re_path به FormReportConsumer وصل کن:
      r"^ws/reports/forms/(?P<uuid>[0-9a-f-]+)/$"
config/asgi.py مستقیماً این متغیر را import می‌کند — نامش را عوض نکن.
"""

websocket_urlpatterns: list = []
