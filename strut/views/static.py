import mimetypes
import os.path
import posixpath

from django.contrib.staticfiles import finders
from django.http import (
    FileResponse,
    HttpResponse,
    HttpResponseNotFound,
    HttpResponseNotModified,
)
from django.utils.http import http_date, parse_http_date_safe
from django.views import View


class Static(View):
    CORS_TYPES = {
        # 'application/javascript',
        "application/x-font-ttf",
        "application/x-font-otf",
        "application/vnd.ms-fontobject",
        "application/font-woff",
        "application/font-woff2",
    }

    def __init__(self):
        mimetypes.add_type("application/font-woff2", ".woff2")

    def get(self, request, path):
        normalized_path = posixpath.normpath(path).lstrip("/")
        absolute_path = finders.find(normalized_path)
        if not absolute_path:
            return HttpResponseNotFound(
                f"'{path}' could not be found", content_type="text/plain"
            )

        content_type, encoding = mimetypes.guess_type(absolute_path)
        try:
            fp = open(absolute_path, "rb")
        except IsADirectoryError:
            return HttpResponseNotFound(
                "Directory indexes are not allowed here.", content_type="text/plain"
            )

        # Handle 304 response
        mtime = http_date(int(os.path.getmtime(absolute_path)))
        if_modified_since = request.META.get("HTTP_IF_MODIFIED_SINCE")
        if if_modified_since and mtime == if_modified_since:
            return HttpResponseNotModified()

        response = FileResponse(fp, content_type=content_type)
        response["Last-Modified"] = mtime
        response["Cache-Control"] = "must-revalidate"
        response["Vary"] = "Accept-Encoding"
        if encoding:
            response["Content-Encoding"] = encoding
        if content_type in self.CORS_TYPES:
            response["Access-Control-Allow-Origin"] = "*"
        return response
