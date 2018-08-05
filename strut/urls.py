from django.conf import settings
from django.urls import include, re_path as path

from .views import agent, api, hooks, static, ui

v0_urls = [
    path(
        "^agent/",
        include(
            [
                path("^ping/$", agent.Ping.as_view()),
                path("^bootstrap/$", agent.Bootstrap.as_view()),
                path("^firmware/$", agent.Firmware.as_view()),
            ]
        ),
    ),
    path("^songmeta/", include([path("^$", api.SongMetaView.as_view())])),
    path("^song/", include([path("^$", api.SongView.as_view())])),
]

hooks_urls = [path("^lockitron/$", hooks.Lockitron.as_view())]

urlpatterns = [
    path("^$", ui.Index.as_view(), name="index"),
    path("^dashboard/$", ui.Dashboard.as_view(), name="dashboard"),
    path("^device-setup/$", ui.DeviceSetup.as_view(), name="device-setup"),
    path("^login/$", ui.Login.as_view(), name="login"),
    path("^logout/$", ui.Logout.as_view(), name="logout"),
    path(
        "^api/",
        include([path("^0/", include(v0_urls)), path("^hooks/", include(hooks_urls))]),
    ),
    path(
        "^%s" % settings.STATIC_URL.lstrip("/"),
        include([path("^(?P<path>.*)$", static.Static.as_view())]),
    ),
    path("", include("social_django.urls", namespace="social")),
]
