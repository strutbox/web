from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.generic import View

from strut.models import (
    Playlist,
    PlaylistSong,
    PlaylistSubscription,
    Song,
    SongJob,
    SongMeta,
)
from strut.schemas.music import SongJobSchema, SongMetaSchema, SongSchema


@method_decorator(login_required, name="dispatch")
class ApiView(View):
    def respond(self, context, status=200):
        context["status"] = status
        return JsonResponse(context, status=status)

    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except Exception as e:
            return self.respond({"error": str(e)}, status=500)


class SongMetaView(ApiView):
    def get(self, request):
        source = int(request.GET["source"])
        identifier = request.GET["identifier"]
        meta = SongMeta.objects.get_or_create(source=source, identifier=identifier)[0]

        try:
            meta.resolver.sync()
        except meta.DataUnsynced as e:
            return self.respond({"error": str(e)}, status=404)

        context = {"songmeta": SongMetaSchema().dump(meta)}
        return self.respond(context)


class SongView(ApiView):
    def get(self, request):
        songs = (
            Song.objects.filter(
                playlistsong__playlist__owner=request.user, file__isnull=False
            )
            .distinct()
            .select_related("meta", "file")
            .order_by("-id")
        )
        return self.respond({"songs": SongSchema(many=True).dump(songs)})

    def post(self, request):
        source = int(request.POST["source"])
        identifier = request.POST["identifier"]
        start = int(request.POST["start"])
        length = int(request.POST["length"])

        try:
            meta = SongMeta.objects.get(source=source, identifier=identifier)
        except SongMeta.DoesNotExist:
            return self.respond({"error": "SongMeta does not exist"}, status=404)

        song = Song.objects.get_or_create(meta=meta, start=start, length=length)[0]
        song.meta = meta

        playlist, created = Playlist.objects.get_or_create(owner=request.user)
        if created:
            PlaylistSubscription.objects.create(user=request.user, playlist=playlist)
        PlaylistSong.objects.create(playlist=playlist, song=song)

        return self.respond({})


class SongDetailView(ApiView):
    def delete(self, request, song_id):
        song_id = int(song_id)

        playlist, created = Playlist.objects.get_or_create(owner=request.user)
        if created:
            PlaylistSubscription.objects.create(user=request.user, playlist=playlist)
        PlaylistSong.objects.filter(playlist=playlist, song_id=song_id).delete()

        return self.respond({})


class SongJobView(ApiView):
    def get(self, request):
        jobs = SongJob.objects.filter(
            user=request.user,
            status__in=[SongJob.Status.New, SongJob.Status.InProgress],
        ).order_by("-date_created")
        return self.respond({"jobs": SongJobSchema(many=True).dump(jobs)})
