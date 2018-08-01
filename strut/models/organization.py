import enum

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models

from strut.db.models import Model, sane_repr


class OrganizationManager(models.Manager):
    def find_and_join(self, user):
        try:
            org = self.get(
                organizationdomain__domain=user.email.split("@", 1)[1].lower()
            )
        except self.model.DoesNotExist:
            return None, False

        return OrganizationMember.objects.get_or_create(organization=org, user=user)


class Organization(Model):
    name = models.TextField()
    slug = models.SlugField()
    settings = JSONField(null=True)
    date_created = models.DateTimeField(auto_now_add=True)

    objects = OrganizationManager()

    __repr__ = sane_repr("name", "slug")

    class Meta:
        unique_together = ("slug",)

    def associate_device(self, device):
        from strut.models import DeviceAssociation

        return DeviceAssociation.objects.get_or_create(organization=self, device=device)


class OrganizationMember(Model):
    @enum.unique
    class Role(enum.IntEnum):
        Owner = 0
        Member = 10

    organization = models.ForeignKey(Organization, models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE)
    is_active = models.BooleanField(default=True)
    role = models.PositiveSmallIntegerField(
        choices=[(r.name, r.value) for r in Role], default=Role.Member.value
    )
    date_joined = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("organization", "user")


class OrganizationDomain(Model):
    organization = models.ForeignKey(Organization, models.CASCADE)
    domain = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)

    __repr__ = sane_repr("organization_id", "domain")

    class Meta:
        unique_together = ("domain",)
