import os
import re
import shutil
from http.cookiejar import CookiePolicy
from tempfile import NamedTemporaryFile, mkstemp
from time import sleep
from urllib.parse import parse_qsl

import rapidjson as json
import requests
from django.utils import timezone
from youtube_dl import YoutubeDL
from youtube_dl.downloader.http import HttpFD
from youtube_dl.extractor.youtube import YoutubeIE
from youtube_dl.utils import ExtractorError

AUDIO_ITAGS = {
    "46",
    "100",
    "101",
    "102",
    "127",
    "128",
    "139",
    "140",
    "141",
    "171",
    "172",
    "249",
    "250",
    "251",
}

RANKING = {"vorbis": 2, "aac": 3, "opus": 4}


class YouTubeResolver:
    def __init__(self, meta, job=None):
        self.meta = meta
        self.job = job

        if self.job is None:
            from strut.models import FakeSongJob

            self.job = FakeSongJob()

    def sync(self, force=False, save=True):
        if not force and self.meta.is_complete:
            return self.meta.data

        info = {}

        dl = YoutubeDL()
        ie = YoutubeIE(dl)

        try:
            info = ie.extract(f"https://youtube.com/watch?v={self.meta.identifier}")
        except ExtractorError as e:
            raise type(self.meta).DataUnsynced(str(e))

        if save:
            # Prevent saving the formats object since it is time sensitive
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

        formats = []
        # print(info['formats'])
        try:
            for fmt in info["formats"]:
                # print(fmt)
                if fmt["format_id"] not in AUDIO_ITAGS:
                    continue
                fmt["_weight"] = fmt["abr"] + RANKING.get(fmt["acodec"], 1) / 10
                formats.append(fmt)
        except KeyError:
            pass

        if not sort:
            return formats

        return sorted(formats, key=lambda f: f["_weight"], reverse=True)

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
        return f"https://img.youtube.com/vi/{self.meta.identifier}/0.jpg"

    def fetch(self):
        fmt = self.get_audio_formats()[0]

        dl = YoutubeDL()
        downloader = HttpFD(dl, {"noprogress": True})

        _, path = mkstemp()
        os.unlink(path)

        downloader.download(path, fmt)
        return path
