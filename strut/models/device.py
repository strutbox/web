import enum
import zlib
from time import time
from uuid import uuid1

import msgpack
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from django.contrib.postgres.fields import JSONField
from django.db import models
from structlog import get_logger

from strut.db.models import Model

logger = get_logger()
channel_layer = get_channel_layer()


class Device(Model):
    name = models.TextField()
    serial = models.CharField(max_length=16)
    pubkey = models.BinaryField()
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("serial",)

    def public_key(self):
        return serialization.load_der_public_key(
            bytes(self.pubkey), backend=default_backend()
        )

    def log(self, request, type, message=None):
        logger.error(DeviceActivity.Type(type).name, device_id=self.id, message=message)

        return DeviceActivity.objects.create(
            device=self,
            type=type,
            message=message,
            ip_address=request.META["REMOTE_ADDR"],
        )

    def encrypt_bytes(self, data):
        return self.public_key().encrypt(
            data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA1()),
                algorithm=hashes.SHA1(),
                label=None,
            ),
        )

    def build_message(self, data):
        data["id"] = uuid1().bytes
        data["time"] = int(time() * 1000)
        return self.encrypt_bytes(zlib.compress(msgpack.packb(data)))

    def send_message(self, message):
        assert self.serial
        async_to_sync(channel_layer.group_send)(
            self.serial, {"type": "device.send", "bytes": self.build_message(message)}
        )


class DeviceAssociation(Model):
    organization = models.ForeignKey("Organization", models.CASCADE)
    device = models.OneToOneField(Device, models.CASCADE, primary_key=True)
    date_added = models.DateTimeField(auto_now_add=True)


class DeviceActivity(Model):
    @enum.unique
    class Type(enum.IntEnum):
        API_PING = 0
        API_BOOTSTRAP = 1

    device = models.ForeignKey(Device, models.CASCADE)
    type = models.PositiveSmallIntegerField(
        choices=[(t.name, t.value) for t in Type], db_index=True
    )
    message = JSONField(null=True)
    ip_address = models.GenericIPAddressField()
    datetime = models.DateTimeField(auto_now_add=True, db_index=True)


def send_message_by_serial(serial, message):
    device = Device.objects.get(serial=serial)
    device.send_message(message)
