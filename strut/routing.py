from channels.routing import ProtocolTypeRouter, URLRouter
from django.conf.urls import re_path as path

from strut.consumers import DeviceConsumer, NullHttpConsumer, NullSocketConsumer

application = ProtocolTypeRouter(
    {
        "http": URLRouter([path(r"", NullHttpConsumer)]),
        "websocket": URLRouter(
            [
                path(r"^(?P<channel>.+)$", DeviceConsumer),
                path(r"^$", NullSocketConsumer),
            ]
        ),
    }
)
