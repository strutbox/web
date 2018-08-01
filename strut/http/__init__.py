from django.http import HttpResponse


class DeviceResponse(HttpResponse):
    def __init__(self, device, data, **kwargs):
        kwargs["content_type"] = "application/octet-stream"
        super().__init__(content=device.build_message(data), **kwargs)
