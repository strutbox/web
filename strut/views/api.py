from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.generic import View

from strut.models import Playlist, PlaylistSong, Song, SongMeta
from strut.schemas.music import SongMetaSchema, SongSchema


@method_decorator(login_required, name="dispatch")
class ApiView(View):
    def respond(self, context, status=200):
        context["status"] = status
        return JsonResponse(context, status=status)

    def dispatch(self, request):
        try:
            return super().dispatch(request)
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

        playlist = Playlist.objects.get(owner=request.user)
        PlaylistSong.objects.create(playlist=playlist, song=song)

        if not song.is_active:
            job = song.process(user=request.user)
        else:
            job = None

        # context = {
        #     'song': SongSchema().dump(song).data,
        #     'job': SongJobSchema().dump(job).data,
        # }

        return self.respond({})
