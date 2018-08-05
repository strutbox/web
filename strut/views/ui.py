from django.conf import settings
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.views.generic import View

from strut.models import OrganizationMember, PlaylistSubscription, Song, SongJob
from strut.schemas.music import PlaylistSubscriptionSchema, SongJobSchema, SongSchema
from strut.schemas.organization import OrganizationMemberSchema
from strut.schemas.user import UserSchema


class Login(View):
    def get(self, request):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse("index"))
        return HttpResponseRedirect(reverse("social:begin", args=("google-oauth2",)))


class Logout(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse("index"))
        return TemplateResponse(request, "logout.html")

    def post(self, request):
        logout(request)
        return HttpResponseRedirect(reverse("index"))


class Index(View):
    def get(self, request):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse("dashboard"))
        return TemplateResponse(request, "index.html")


class Dashboard(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse("index"))

        memberships = (
            OrganizationMember.objects.filter(user=request.user, is_active=True)
            .select_related("organization")
            .order_by("-id")
        )

        playlists = (
            PlaylistSubscription.objects.filter(user=request.user, is_active=True)
            .exclude(playlist__owner=request.user)
            .select_related("playlist")
        )

        songs = (
            Song.objects.filter(
                playlistsong__playlist__owner=request.user, file__isnull=False
            )
            .select_related("meta", "file")
            .order_by("-id")
        )

        jobs = SongJob.objects.filter(
            user=request.user,
            status__in=[SongJob.Status.New, SongJob.Status.InProgress],
        ).order_by("-date_created")

        context = {
            "settings": {"static": settings.STATIC_URL},
            "initial_data": {
                "user": UserSchema().dump(request.user),
                "memberships": OrganizationMemberSchema(many=True).dump(memberships),
                "playlists": PlaylistSubscriptionSchema(many=True).dump(playlists),
                "songs": SongSchema(many=True).dump(songs),
                "jobs": SongJobSchema(many=True).dump(jobs),
            },
        }
        return TemplateResponse(request, "dashboard.html", context=context)


class DeviceSetup(View):
    def get(self, request):
        return TemplateResponse(request, "setup.html")
