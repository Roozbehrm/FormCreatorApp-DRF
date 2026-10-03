from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from rest_framework_simplejwt.authentication import JWTAuthentication


class FormReportConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.form = await self._get_form()
        user = self.scope["user"]
        if user.is_anonymous:
            user = await self._authenticate_bearer_token()
        if self.form is None or not user or user.is_anonymous or self.form.owner_id != user.id:
            await self.close(code=4403)
            return

        self.group_name = f"report.form.{self.form.uuid}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.send_json(await self._get_report())

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def report_update(self, event):
        await self.send_json(event["payload"])

    @database_sync_to_async
    def _get_form(self):
        from apps.forms.models import Form

        try:
            return Form.objects.get(uuid=self.scope["url_route"]["kwargs"]["uuid"])
        except Form.DoesNotExist:
            return None

    @database_sync_to_async
    def _authenticate_bearer_token(self):
        from apps.accounts.authentication import ACCESS_TOKEN_COOKIE

        token = self.scope.get("cookies", {}).get(ACCESS_TOKEN_COOKIE)
        if not token:
            authorization = dict(self.scope.get("headers", [])).get(b"authorization", b"").decode("utf-8")
            parts = authorization.split()
            if len(parts) != 2 or parts[0].lower() != "bearer":
                return None
            token = parts[1]
        try:
            authentication = JWTAuthentication()
            validated_token = authentication.get_validated_token(token)
            return authentication.get_user(validated_token)
        except Exception:
            return None

    @database_sync_to_async
    def _get_report(self):
        from .services import form_report

        return form_report(self.form)
