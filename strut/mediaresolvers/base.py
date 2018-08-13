class BaseMediaResolver:
    def __init__(self, meta, job=None):
        self.meta = meta
        self.job = job

        if self.job is None:
            from strut.models import FakeSongJob

            self.job = FakeSongJob()

    def bind_job(self, job):
        self.job = job

    @property
    def duration(self):
        try:
            return int(self.meta.data["duration"])
        except (TypeError, LookupError):
            raise type(self.meta).DataUnsynced()

    @property
    def title(self):
        try:
            return self.meta.data["title"]
        except (TypeError, LookupError):
            raise type(self.meta).DataUnsynced()

    @property
    def thumbnail(self):
        raise NotImplementedError

    def fetch(self):
        raise NotImplementedError
