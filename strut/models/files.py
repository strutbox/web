import base64
import hashlib
import os

from django.conf import settings
from django.db import models

from strut.db.models import Model, sane_repr


def shasums(f, algorithms=("md5", "sha256")):
    start = f.tell()
    f.seek(0)
    sums = tuple(hashlib.new(a) for a in algorithms)
    for chunk in iter(lambda: f.read(4096), b""):
        for sum in sums:
            sum.update(chunk)
    f.seek(start)
    return sums


_bucket = None


def get_bucket():
    global _bucket
    if _bucket is None:
        from google.cloud.storage.client import Client

        # A `None` project behaves differently with the client, so
        # we need to call it differently
        try:
            client = Client(project=os.environ["GOOGLE_CLOUD_PROJECT"])
        except KeyError:
            client = Client()
        _bucket = client.bucket(settings.GOOGLE_STORAGE_BUCKET)
    return _bucket


class FileQuerySet(models.QuerySet):
    def delete(self):
        raise NotImplementedError


class FileManager(models.Manager):
    def get_queryset(self):
        return FileQuerySet(self.model, using=self._db)

    def upload_from_filename(self, filepath):
        with open(filepath, "rb") as fp:
            return self.upload(fp)

    def upload(self, fp):
        md5sum, sha256sum = shasums(fp)

        try:
            return self.get(checksum=sha256sum.digest())
        except self.model.DoesNotExist:
            pass

        blob = get_bucket().blob(f"files/{sha256sum.hexdigest()}")
        blob.md5_hash = base64.b64encode(md5sum.digest()).decode()
        blob.upload_from_file(fp, predefined_acl="publicRead")
        return self.get_or_create(
            checksum=sha256sum.digest(),
            defaults={"size": blob.size, "time_created": blob.time_created},
        )[0]

    def delete(self):
        raise NotImplementedError


class File(Model):
    checksum = models.BinaryField()
    size = models.PositiveIntegerField()
    time_created = models.DateTimeField()

    objects = FileManager()

    __repr__ = sane_repr("id", "hexdigest")

    class Meta:
        unique_together = ("checksum",)

    def hexdigest(self):
        d = self.checksum
        if isinstance(d, memoryview):
            d = bytes(d)
        return d.hex()

    def get_public_url(self):
        return f"https://{settings.GOOGLE_STORAGE_BUCKET}.storage.googleapis.com/files/{self.hexdigest()}"

    def delete(self):
        from google.cloud.exceptions import NotFound

        try:
            get_bucket().delete_blob(self.hexdigest())
        except NotFound:
            pass
        return super().delete()
