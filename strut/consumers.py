import asyncio

import msgpack
from channels.db import database_sync_to_async
from channels.generic.http import AsyncHttpConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.signing import BadSignature, TimestampSigner
from structlog import get_logger

from strut.models import Device, DeviceActivity

logger = get_logger()


class DeviceConsumer(AsyncWebsocketConsumer):
    device = None

    async def connect(self):
        channel = self.scope["url_route"]["kwargs"]["channel"]
        try:
            device_serial = TimestampSigner().unsign(channel, max_age=30)
        except BadSignature:
            logger.error("connect.reject", channel=channel)
            await self.close(code=404)
            return

        try:
            self.device = await get_device_by_serial(device_serial)
        except Device.DoesNotExist:
            logger.error("connect.reject", serial=device_serial)
            await self.close(code=404)
            return

        await asyncio.wait(
            [
                self.channel_layer.group_add(self.device.serial, self.channel_name),
                self.channel_layer.group_add("alldevices", self.channel_name),
                device_log(self.device, DeviceActivity.Type.WS_CONNECT, self.scope),
            ]
        )
        logger.error("connect.accept", device_id=self.device.id)
        await self.accept()

    async def disconnect(self, code):
        if self.device:
            logger.error("disconnect", device_id=self.device.id)
            await asyncio.wait(
                [
                    self.channel_layer.group_discard("alldevices", self.channel_name),
                    self.channel_layer.group_discard(
                        self.device.serial, self.channel_name
                    ),
                    device_log(
                        self.device, DeviceActivity.Type.WS_DISCONNECT, self.scope
                    ),
                ]
            )

    async def receive(self, text_data=None, bytes_data=None):
        if text_data is not None:
            return
        try:
            msg = msgpack.unpackb(bytes_data, raw=False)
        except Exception as e:
            print(e)
            return

        logger.error("receive", device_id=self.device_id, message=msg)

    async def device_send(self, event):
        if "text" in event:
            await self.send(text_data=event["text"])
        else:
            await self.send(bytes_data=event["bytes"])


class NullSocketConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.close(code=404)


class NullHttpConsumer(AsyncHttpConsumer):
    async def handle(self, body):
        await self.send_response(204, b"", headers=[])


@database_sync_to_async
def get_device_by_serial(serial):
    return Device.objects.get(serial=serial)


class FakeRequest:
    def __init__(self, client):
        self.META = {"REMOTE_ADDR": client[0]}


@database_sync_to_async
def device_log(device, type, scope):
    device.log(FakeRequest(scope.get("client", ["0.0.0.0"])), type)
