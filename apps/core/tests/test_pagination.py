import pytest
from django.test import RequestFactory
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request

from apps.core.pagination import StandardPagination


def test_default_page_size_is_twenty():
  paginator = StandardPagination()
  request = Request(RequestFactory().get("/"))
  page = paginator.paginate_queryset(list(range(25)), request)

  assert paginator.page_size == 20
  assert len(page) == 20


def test_page_size_query_parameter_is_used():
  paginator = StandardPagination()
  request = Request(RequestFactory().get("/?page_size=7"))
  page = paginator.paginate_queryset(list(range(25)), request)

  assert len(page) == 7


@pytest.mark.parametrize("page_size", ["0", "101", "not-a-number"])
def test_invalid_page_size_is_rejected(page_size):
  paginator = StandardPagination()

  with pytest.raises(ValidationError):
    request = Request(RequestFactory().get(f"/?page_size={page_size}"))
    paginator.paginate_queryset(list(range(25)), request)
