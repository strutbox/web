from social_core.exceptions import AuthForbidden

from strut.models import OrganizationDomain


def auth_allowed(strategy, details, backend, user=None, *args, **kwargs):
    email = details.get("email")
    if email:
        if not OrganizationDomain.objects.filter(
            domain=email.split("@", 1)[1].lower()
        ).exists():
            raise AuthForbidden(backend)
