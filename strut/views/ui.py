from django.conf import settings
from django.contrib.auth import logout
from django.http import Http404, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.views.generic import View

from strut.models import OrganizationMember, PlaylistSubscription, Song, User
from strut.schemas.music import PlaylistSubscriptionSchema, SongSchema
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

        context = {}
        if request.GET.get("error") == "forbidden":
            context["error"] = "You're not allowed to sign up. Try a different email."
        return TemplateResponse(request, "index.html", context=context)


class AppView(View):
    script = None

    def has_permission(self, request):
        return True

    def get(self, request, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse("index"))

        if not self.has_permission(request):
            raise Http404

        context = {
            "script": self.script,
            "settings": {"static": settings.STATIC_URL},
            "initial_data": self.get_initial_data(request),
        }
        return TemplateResponse(request, "app.html", context=context)

    def get_initial_data(self, request):
        return {"me": UserSchema().dump(request.user)}


class Dashboard(AppView):
    script = "dashboard.js"

    def get_initial_data(self, request):
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

        return {
            **super().get_initial_data(request),
            **{
                "memberships": OrganizationMemberSchema(many=True).dump(memberships),
                "playlists": PlaylistSubscriptionSchema(many=True).dump(playlists),
            },
        }


class OrganizationMembersView(AppView):
    script = "organizationMembers.js"

    def has_permission(self, request):
        return OrganizationMember.objects.filter(
            user=request.user, organization__slug=self.kwargs["organization_slug"]
        ).exists()

    def get_initial_data(self, request):
        users = (
            User.objects.filter(
                organizationmember__organization__slug=self.kwargs["organization_slug"],
                organizationmember__is_active=True,
            )
            .exclude(id=request.user.id)
            .order_by("-id")
        )
        return {
            **super().get_initial_data(request),
            **{"members": UserSchema(many=True).dump(users)},
        }


class UserDetailsView(AppView):
    script = "userDetails.js"

    def has_permission(self, request):
        return User.objects.filter(
            email=self.kwargs["email"],
            organizationmember__organization__in=OrganizationMember.objects.filter(
                user=request.user, is_active=True
            ).values_list("organization_id"),
            organizationmember__is_active=True,
        ).exists()

    def get_initial_data(self, request):
        user = User.objects.get(email=self.kwargs["email"])
        songs = (
            Song.objects.filter(playlistsong__playlist__owner=user, file__isnull=False)
            .distinct()
            .select_related("meta", "file")
            .order_by("-id")
        )
        return {
            **super().get_initial_data(request),
            **{
                "user": UserSchema().dump(user),
                "songs": SongSchema(many=True).dump(songs),
            },
        }


class DeviceSetup(View):
    def get(self, request):
        return TemplateResponse(request, "setup.html")
