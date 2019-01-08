from django.conf import settings
from django.urls import include, re_path as path
from django.views.generic.base import RedirectView

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
    path(
        "^song/",
        include(
            [
                path("^$", api.SongView.as_view()),
                path("^(?P<song_id>\d+)/$", api.SongDetailView.as_view()),
            ]
        ),
    ),
    path("^songjob/", include([path("^$", api.SongJobView.as_view())])),
    path("^user/", include([path("^settings/$", api.UserSettingsView.as_view())])),
]

hooks_urls = [path("^lockitron/$", hooks.Lockitron.as_view())]

urlpatterns = [
    path("^$", ui.Index.as_view(), name="index"),
    path(
        "^favicon\.ico$", RedirectView.as_view(url=f"{settings.STATIC_URL}favicon.png")
    ),
    path("^dashboard/$", ui.Dashboard.as_view(), name="dashboard"),
    path(
        "^users/", include([path("^(?P<email>[^\/]+)/$", ui.UserDetailsView.as_view())])
    ),
    path(
        "^organization/",
        include(
            [
                path(
                    "^(?P<organization_slug>[a-z-]+)/members/$",
                    ui.OrganizationMembersView.as_view(),
                )
            ]
        ),
    ),
    path("^login/$", ui.Login.as_view(), name="login"),
    path("^logout/$", ui.Logout.as_view(), name="logout"),
    path(
        "^api/",
        include([path("^0/", include(v0_urls)), path("^hooks/", include(hooks_urls))]),
    ),
    path(
        f"^{settings.STATIC_URL.lstrip('/')}",
        include([path("^(?P<path>.*)$", static.Static.as_view(), name="static")]),
    ),
    path("^device-setup/$", ui.DeviceSetup.as_view(), name="device-setup"),
    path("", include("social_django.urls", namespace="social")),
]
