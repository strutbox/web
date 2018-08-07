import shutil
from tempfile import NamedTemporaryFile
from urllib.parse import parse_qs

import requests

AUDIO_ITAGS = {
    "46": {"encoding": "vorbis", "bitrate": 192},
    "100": {"encoding": "vorbis", "bitrate": 128},
    "101": {"encoding": "vorbis", "bitrate": 192},
    "102": {"encoding": "vorbis", "bitrate": 192},
    "127": {"encoding": "aac", "bitrate": 96},
    "128": {"encoding": "aac", "bitrate": 96},
    "139": {"encoding": "aac", "bitrate": 48},
    "140": {"encoding": "aac", "bitrate": 128},
    "141": {"encoding": "aac", "bitrate": 256},
    "171": {"encoding": "vorbis", "bitrate": 128},
    "172": {"encoding": "vorbis", "bitrate": 192},
    "249": {"encoding": "opus", "bitrate": 48},
    "250": {"encoding": "opus", "bitrate": 64},
    "251": {"encoding": "opus", "bitrate": 160},
}

RANKING = {"vorbis": 2, "aac": 3, "opus": 4}


class YouTube:
    @staticmethod
    def download(id):
        s = requests.Session()

        resp = s.get(
            "https://www.youtube.com/get_video_info",
            params={"video_id": id, "ps": "default", "gl": "US", "hl": "en"},
        )
        resp.raise_for_status()
        info = parse_qs(resp.text)
        formats = []

        for k in "url_encoded_fmt_stream_map", "adaptive_fmts":
            for fmt in info.pop(k, []):
                formats += fmt.split(",")

        url = sorted(
            map(
                lambda f: (
                    AUDIO_ITAGS[f["itag"][0]]["bitrate"]
                    + RANKING[AUDIO_ITAGS[f["itag"][0]]["encoding"]] / 10,
                    f,
                ),
                filter(lambda f: f["itag"][0] in AUDIO_ITAGS, map(parse_qs, formats)),
            ),
            key=lambda f: f[0],
            reverse=True,
        )[0][1]["url"][0]

        with s.get(url, stream=True) as r:
            r.raise_for_status()
            fp = NamedTemporaryFile()
            shutil.copyfileobj(r.raw, fp)
        return fp
