import asyncio

from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.signing import BadSignature, TimestampSigner

from strut.models import Device


class DeviceConsumer(AsyncWebsocketConsumer):
    device = None

    async def connect(self):
        channel = self.scope["url_route"]["kwargs"]["channel"]
        try:
            device_serial = TimestampSigner().unsign(channel, max_age=30)
        except BadSignature:
            await self.close(code=404)
            return

        try:
            self.device = await get_device_by_serial(device_serial)
        except Device.DoesNotExist:
            await self.close(code=404)
            return

        await asyncio.wait(
            [
                self.channel_layer.group_add(self.device.serial, self.channel_name),
                self.channel_layer.group_add("alldevices", self.channel_name),
            ]
        )
        await self.accept()

    async def disconnect(self, code):
        if self.device:
            await asyncio.wait(
                [
                    self.channel_layer.group_discard("alldevices", self.channel_name),
                    self.channel_layer.group_discard(
                        self.device.serial, self.channel_name
                    ),
                ]
            )

    async def receive(self, text_data):
        print(text_data, self.channel_name)

    async def device_send(self, event):
        if "text" in event:
            await self.send(text_data=event["text"])
        else:
            await self.send(bytes_data=event["bytes"])


class NullConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.close(code=404)


@database_sync_to_async
def get_device_by_serial(serial):
    return Device.objects.get(serial=serial)
