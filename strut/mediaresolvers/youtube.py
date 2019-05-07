from youtube_dl import YoutubeDL
from youtube_dl.extractor.youtube import YoutubeIE

from .base import BaseMediaResolver

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


class YouTubeResolver(BaseMediaResolver):
    def extract(self):
        ie = YoutubeIE(YoutubeDL())

        return ie.extract(f"https://youtube.com/watch?v={self.meta.identifier}")

    def extract_audio_formats(self, info, sort=True):
        formats = []
        try:
            for fmt in info["formats"]:
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
    def thumbnail(self):
        return f"https://img.youtube.com/vi/{self.meta.identifier}/0.jpg"
