import pytest
from asgiref.sync import async_to_sync
from channels.testing import WebsocketCommunicator
from rest_framework_simplejwt.tokens import RefreshToken

from config.asgi import application


@pytest.mark.django_db(transaction=True)
def test_report_websocket_authenticates_with_access_cookie(user, form):
    access_token = str(RefreshToken.for_user(user).access_token)
    communicator = WebsocketCommunicator(
        application,
        f"/ws/reports/forms/{form.uuid}/",
        headers=[
            (b"cookie", f"access={access_token}".encode()),
            (b"origin", b"http://testserver"),
        ],
    )

    async def connect_and_receive():
        connected, _ = await communicator.connect()
        assert connected
        payload = await communicator.receive_json_from()
        assert payload["form_id"] == form.id
        await communicator.disconnect()

    async_to_sync(connect_and_receive)()
