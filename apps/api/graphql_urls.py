import strawberry
from django.urls import path
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.request import Request as DRFRequest
from strawberry.django.views import GraphQLView
from strawberry.scalars import JSON
from strawberry.types import Info

from apps.accounts.authentication import CookieJWTAuthentication
from apps.forms.models import Form
from apps.processes.models import Process
from apps.reports.services import form_report as build_form_report
from apps.reports.services import process_report as build_process_report


def _authenticated_user(request):
	authentication = CookieJWTAuthentication().authenticate(DRFRequest(request))
	if authentication is None:
		raise AuthenticationFailed("Authentication is required.")
	return authentication[0]


@strawberry.type
class ReportQuery:
	@strawberry.field
	def form_report(self, info: Info, uuid: str) -> JSON:
		user = _authenticated_user(info.context.request)
		form = Form.objects.filter(uuid=uuid, owner=user).first()
		if form is None:
			raise AuthenticationFailed("Form not found.")
		return build_form_report(form)

	@strawberry.field
	def process_report(self, info: Info, uuid: str) -> JSON:
		user = _authenticated_user(info.context.request)
		process = Process.objects.filter(uuid=uuid, owner=user).first()
		if process is None:
			raise AuthenticationFailed("Process not found.")
		return build_process_report(process)


schema = strawberry.Schema(query=ReportQuery)

urlpatterns = [path("", GraphQLView.as_view(schema=schema), name="graphql")]
