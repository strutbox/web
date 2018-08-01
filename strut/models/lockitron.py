from django.db import models

from strut.db.models import Model, sane_repr


class LockitronLock(Model):
    organization = models.ForeignKey("Organization", models.CASCADE)
    lock_id = models.TextField()
    name = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("lock_id",)


class LockitronUser(Model):
    lock = models.ForeignKey(LockitronLock, models.CASCADE)
    user_id = models.TextField()
    email = models.TextField()
    first_name = models.TextField(null=True)
    last_name = models.TextField(null=True)
    date_created = models.DateTimeField(auto_now_add=True)

    __repr__ = sane_repr("lock_id", "user_id", "email")

    class Meta:
        unique_together = ("user_id",)
