from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import ValidationError


class StandardPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_page_size(self, request):
        raw_page_size = request.query_params.get(self.page_size_query_param)
        if raw_page_size in (None, ""):
            return self.page_size
        try:
            page_size = int(raw_page_size)
        except (TypeError, ValueError) as exc:
            raise ValidationError({"page_size": "page_size must be an integer."}) from exc
        if page_size < 1 or page_size > self.max_page_size:
            raise ValidationError({"page_size": f"page_size must be between 1 and {self.max_page_size}."})
        return page_size
