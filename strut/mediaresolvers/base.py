import os
from tempfile import mkstemp

from django.utils import timezone
from youtube_dl import YoutubeDL
from youtube_dl.downloader.http import HttpFD
from youtube_dl.utils import ExtractorError


class BaseMediaResolver:
    def __init__(self, meta, job=None):
        self.meta = meta
        self.job = job

        if self.job is None:
            from strut.models import FakeSongJob

            self.job = FakeSongJob()

    def bind_job(self, job):
        self.job = job

    @property
    def duration(self):
        try:
            return int(self.meta.data["duration"])
        except (TypeError, LookupError):
            raise type(self.meta).DataUnsynced()

    @property
    def title(self):
        try:
            return self.meta.data["title"]
        except (TypeError, LookupError):
            raise type(self.meta).DataUnsynced()

    @property
    def thumbnail(self):
        raise NotImplementedError

    def sync(self, force=False, save=True):
        if not force and self.meta.is_complete:
            return self.meta.data

        try:
            info = self.extract()
        except ExtractorError as e:
            raise type(self.meta).DataUnsynced(str(e))

        if save:
            formats = info.pop("formats")
            self.meta.data = info
            self.meta.last_synced = timezone.now()
            self.meta.save()
            info["formats"] = formats

        return info

    def get_audio_formats(self, sort=True):
        # We can't use the cached data for this, the url needs to be generated
        # from YouTube because it expires
        info = self.sync(force=True, save=False)

        return self.extract_audio_formats(info, sort=sort)

    def extract_audio_formats(info, sort=True):
        raise NotImplementedError

    def extract(self):
        raise NotImplementedError

    def fetch(self):
        fmt = self.get_audio_formats()[0]

        dl = YoutubeDL()
        downloader = HttpFD(dl, {"noprogress": True})

        _, path = mkstemp()
        os.unlink(path)

        downloader.download(path, fmt)
        return path
