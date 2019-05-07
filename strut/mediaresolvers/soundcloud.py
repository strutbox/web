from youtube_dl import YoutubeDL
from youtube_dl.extractor.soundcloud import SoundcloudIE

from .base import BaseMediaResolver

RANKING = {"mp3": 3, "opus": 4}


class SoundcloudResolver(BaseMediaResolver):
    @property
    def title(self):
        try:
            return f"{self.meta.data['uploader']} - {self.meta.data['title']}"
        except (TypeError, LookupError):
            raise type(self.meta).DataUnsynced()

    def extract(self):
        ie = SoundcloudIE(YoutubeDL())

        return ie.extract(f"https://soundcloud.com/{self.meta.identifier}")

    def extract_audio_formats(self, info, sort=True):
        formats = []
        try:
            for fmt in info["formats"]:
                if not fmt["format_id"].startswith(("http_mp3", "http_opus")):
                    continue
                if "abr" not in fmt:
                    continue
                if fmt["ext"] not in RANKING:
                    continue
                fmt["_weight"] = fmt["abr"] + RANKING[fmt["ext"]] / 10
                formats.append(fmt)
        except KeyError:
            pass

        if not sort:
            return formats

        return sorted(formats, key=lambda f: f["_weight"], reverse=True)

    @property
    def thumbnail(self):
        return self.meta.data["thumbnail"]
