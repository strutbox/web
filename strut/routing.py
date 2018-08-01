from channels.routing import URLRouter
from django.conf.urls import re_path as path

from strut.consumers import DeviceConsumer, NullConsumer

application = URLRouter(
    [path(r"^(?P<channel>.+)$", DeviceConsumer), path(r"^$", NullConsumer)]
)
