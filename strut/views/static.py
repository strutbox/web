import mimetypes
import os.path
import posixpath
from dataclasses import dataclass
from functools import lru_cache
from typing import BinaryIO, Optional

from django.conf import settings
from django.contrib.staticfiles import finders
from django.http import FileResponse, HttpResponseNotFound, HttpResponseNotModified
from django.utils.http import http_date
from django.views import View


class Static(View):
    def __init__(self):
        mimetypes.add_type("application/font-woff2", ".woff2")

    def get(self, request, path):
        return open_fp(path).get_response(request)


CORS_TYPES = {
    # 'application/javascript',
    "application/x-font-ttf",
    "application/x-font-otf",
    "application/vnd.ms-fontobject",
    "application/font-woff",
    "application/font-woff2",
}


@dataclass
class NonClosingFile:
    fp: BinaryIO

    def read(self, size):
        return self.fp.read(size)

    def seek(self, position):
        return self.fp.seek(position)

    def fileno(self):
        return self.fp.fileno()

    def __iter__(self):
        return iter(self.fp)


@dataclass
class ResponseFile:
    fp: NonClosingFile
    content_type: str
    encoding: Optional[str]
    mtime: str

    def get_response(self, request):
        # Handle 304 response
        if_modified_since = request.META.get("HTTP_IF_MODIFIED_SINCE")
        if if_modified_since and self.mtime == if_modified_since:
            return HttpResponseNotModified()

        self.fp.seek(0)
        response = FileResponse(self.fp, content_type=self.content_type)
        response["Last-Modified"] = self.mtime
        response["Cache-Control"] = "must-revalidate"
        response["Vary"] = "Accept-Encoding"
        if self.encoding:
            response["Content-Encoding"] = self.encoding
        if self.content_type in CORS_TYPES:
            response["Access-Control-Allow-Origin"] = "*"
        return response


@dataclass
class FileNotFoundFile:
    path: str

    def get_response(self, request):
        return HttpResponseNotFound(
            f"'{self.path}' could not be found", content_type="text/plain"
        )


@dataclass
class DirectoryResponseFile:
    def get_response(self, request):
        return HttpResponseNotFound(
            "Directory indexes are not allowed here.", content_type="text/plain"
        )


def open_fp(path):
    normalized_path = posixpath.normpath(path).lstrip("/")
    absolute_path = finders.find(normalized_path)
    if not absolute_path:
        return FileNotFoundFile(path)

    content_type, encoding = mimetypes.guess_type(absolute_path)
    try:
        fp = open(absolute_path, "rb")
    except IsADirectoryError:
        return DirectoryResponseFile

    mtime = http_date(int(os.path.getmtime(absolute_path)))
    return ResponseFile(NonClosingFile(fp), content_type, encoding, mtime)


if settings.STATIC_FP_CACHE > 0:
    open_fp = lru_cache(maxsize=settings.STATIC_FP_CACHE)(open_fp)
