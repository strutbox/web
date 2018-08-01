import enum
import time
from uuid import uuid4

import rapidjson as json
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models import Value as V
from django.db.models.functions import Concat
from django.utils import timezone

from strut.db.models import Model, sane_repr
from strut.mediaresolvers.youtube import YouTubeResolver


class SongMeta(Model):
    @enum.unique
    class Source(enum.IntEnum):
        YouTube = 0

    class DataUnsynced(Exception):
        pass

    source = models.PositiveSmallIntegerField(
        choices=[(s.name, s.value) for s in Source]
    )
    identifier = models.TextField()
    data = JSONField(null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    last_synced = models.DateTimeField(null=True, db_index=True)

    class Meta:
        unique_together = ("source", "identifier")

    __repr__ = sane_repr("source", "identifier", "is_complete")

    @property
    def resolver(self):
        if self.source == SongMeta.Source.YouTube:
            return YouTubeResolver(self)
        raise NotImplementedError

    @property
    def is_complete(self):
        return self.data is not None and self.last_synced is not None


class SongQuerySet(models.QuerySet):
    def pick_for_user(self, user):
        return self.pick_for_user_id(user.id)

    def pick_for_user_id(self, user_id):
        return (
            self.filter(
                is_active=True,
                playlistsong__playlist__playlistsubscription__user_id=user_id,
                playlistsong__playlist__playlistsubscription__is_active=True,
                meta__last_synced__isnull=False,
                file__isnull=False,
            )
            .order_by("?")[0:1]
            .get()
        )


class Song(Model):
    meta = models.ForeignKey(SongMeta, models.CASCADE)
    file = models.ForeignKey("File", models.CASCADE, null=True)
    start = models.PositiveIntegerField()
    length = models.PositiveIntegerField()
    date_created = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)

    objects = SongQuerySet.as_manager()

    class Meta:
        unique_together = ("meta", "start", "length")

    __repr__ = sane_repr("meta_id", "file_id", "start", "length")

    def save(self, *args, **kwargs):
        assert self.meta.is_complete
        assert (self.start + self.length) <= self.meta.resolver.duration
        assert self.length > 0
        return super().save(*args, **kwargs)

    def process(self, user=None, force=False, sync=False):
        if not force:
            assert not self.is_active

        sj = SongJob.objects.create(song=self, user=user)

        from strut import tasks

        if sync:
            from strut.tasks.music import process_songjob

            process_songjob(job_id=sj.id)
        else:
            tasks.enqueue(
                func="strut.tasks.music.process_songjob", kwargs={"job_id": sj.id}
            )

        return sj


class Playlist(Model):
    identifier = models.UUIDField(default=uuid4)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, models.SET_NULL, null=True)
    shared = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("identifier",)


class PlaylistSong(Model):
    playlist = models.ForeignKey(Playlist, models.CASCADE)
    song = models.ForeignKey(Song, models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)


class PlaylistSubscription(Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE)
    playlist = models.ForeignKey(Playlist, models.CASCADE)
    is_active = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "playlist")


class SongJob(Model):
    @enum.unique
    class Status(enum.IntEnum):
        New = 0
        InProgress = 1
        Success = 2
        Failure = 3

    song = models.ForeignKey(Song, models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, models.CASCADE, null=True, db_index=True
    )
    status = models.PositiveSmallIntegerField(
        choices=[(s.name, s.value) for s in Status], default=Status.New.value
    )
    log = models.TextField(default="")
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now_add=True)

    def record(self, log=None, status=None):
        update = {"date_updated": timezone.now()}

        if status is not None:
            update["status"] = status

        if log is not None:
            update["log"] = Concat(
                "log",
                V(
                    json.dumps({"t": int(time.time() * 1000), "m": log, "s": status})
                    + "\n"
                ),
            )

        return SongJob.objects.filter(id=self.id).update(**update)

    @property
    def is_complete(self):
        return self.status in (Status.Success, Status.Failure)

    def get_log(self):
        if not self.log:
            return

        return list(map(json.loads, self.log.splitlines()))


class FakeSongJob:
    def record(*args, **kwargs):
        return
