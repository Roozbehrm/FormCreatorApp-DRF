"""
مالک: روزبه (امتیازی)
TODO: FormReportConsumer(AsyncJsonWebsocketConsumer)   مسیر: /ws/reports/forms/<uuid>/
  - connect()      بررسی دسترسی مالک، عضویت در گروه report.form.<uuid>، accept()
  - disconnect()   خروج از گروه
  - report_update(event)   پوش payload جدید (خروجی form_report) به کلاینت متصل
سیگنال ثبت پاسخ در apps/forms/signals.py (با هماهنگی فائزه/علی) باید group_send را صدا بزند.
"""
