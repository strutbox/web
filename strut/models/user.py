# import enum
from django.contrib.auth.models import BaseUserManager
from django.contrib.postgres.fields import JSONField
from django.db import models

from strut.db.models import Model, sane_repr


class UserManager(BaseUserManager):
    def create_user(self, email, **extra_fields):
        # extra_fields.pop('username', None)
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.save(using=self._db)

        from strut.models import Organization

        Organization.objects.find_and_join(user)
        return user


class User(Model):
    email = models.TextField()
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    settings = JSONField(null=True)

    is_authenticated = True
    is_anonymous = False

    objects = UserManager()

    # Make Django happy
    REQUIRED_FIELDS = ()
    USERNAME_FIELD = "email"

    class Meta:
        # Create this explicit UNIQUE on `email` since
        # Django's default behavior for `unique=True` is to
        # also add a stupid text_pattern_ops index which
        # isn't needed because we'll never do LIKE queries
        unique_together = ("email",)

    __repr__ = sane_repr("id", "email")

    def __str__(self):
        return self.email


# class UserActivity(Model):
#     @enum.unique
#     class Type(enum.IntEnum):
#         pass
#
#     datetime = models.DateTimeField(auto_now_add=True, db_index=True)
