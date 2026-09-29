"""
مالک: روزبه (اسکلت اولیه) — سپس فائزه قوانین دقیق اعتبارسنجی هر نوع را تکمیل می‌کند.
TODO: هفت هندلر، هرکدام با FieldRegistry.register ثبت شوند:
  - TextHandler       type="text"       config: min_length, max_length, regex, placeholder
  - TextareaHandler   type="textarea"   config: min_length, max_length, rows
  - NumberHandler     type="number"     config: min, max, step, is_integer, unit
  - SelectHandler     type="select"     config: multiple, allow_other  (+ FieldOption)
  - CheckboxHandler   type="checkbox"   config: min_selected, max_selected  (+ FieldOption)
  - RatingHandler     type="rating"     config: max_value, allow_half, icon
  - DateHandler       type="date"       config: min_date, max_date, include_time
"""
