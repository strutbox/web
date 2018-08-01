import enum

from django.db import models

from strut.db.models import Model


class FirmwareVersion(Model):
    @enum.unique
    class Channel(enum.IntEnum):
        Device = 0

    channel = models.PositiveSmallIntegerField(
        choices=[(c.name, c.value) for c in Channel]
    )
    version = models.TextField()
    name = models.TextField(null=True)
    notes = models.TextField(null=True)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["-date_created"])]
        unique_together = "channel", "version"
        ordering = ("-date_created",)
