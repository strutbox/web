import jsonschema
import rapidjson as json
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse
from django.template.loader import get_template
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from structlog import get_logger

from strut.models import (
    Device,
    LockitronLock,
    LockitronUser,
    OrganizationDomain,
    Song,
    User,
)

logger = get_logger()


@method_decorator(csrf_exempt, name="dispatch")
class HooksView(View):
    pass


USER_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "email": {"type": "string"},
        "first_name": {"type": ["string", "null"]},
        "last_name": {"type": ["string", "null"]},
    },
    "required": ["id", "email"],
}

LOCK_SCHEMA = {
    "type": "object",
    "properties": {"id": {"type": "string"}, "name": {"type": "string"}},
    "required": ["id", "name"],
}

ACTIVITY_SCHEMA = {
    "type": "object",
    "properties": {"id": {"type": "string"}, "kind": {"type": "string"}},
    "required": ["id", "kind"],
}

DATA_SCHEMA = {
    "type": "object",
    "properties": {
        "user": USER_SCHEMA,
        "lock": LOCK_SCHEMA,
        "activity": ACTIVITY_SCHEMA,
    },
    "required": ["user", "lock", "activity"],
}

LOCKITRON_SCHEMA = jsonschema.Draft4Validator(
    {
        "type": "object",
        "properties": {
            "timestamp": {"type": "number"},
            "signature": {"type": "string"},
            "data": DATA_SCHEMA,
        },
        "required": ["timestamp", "data"],
    }
)


class Lockitron(HooksView):
    def post(self, request):
        # log = logger.new(
        #     path_info=request.META['PATH_INFO'],
        #     ip_address=request.META['REMOTE_ADDR'],
        # )

        if request.content_type != "application/json":
            return HttpResponse(status=400)

        try:
            payload = json.loads(request.body)
        except Exception:
            return HttpResponse(status=400)

        try:
            LOCKITRON_SCHEMA.validate(payload)
        except jsonschema.exceptions.ValidationError as e:
            return HttpResponse(str(e), status=400)

        data = payload["data"]
        lock, user, activity = data["lock"], data["user"], data["activity"]
        email = User.objects.normalize_email(user["email"])

        try:
            lockitron_lock = LockitronLock.objects.get(lock_id=lock["id"])
        except LockitronLock.DoesNotExist:
            return HttpResponse(status=404)

        if lockitron_lock.name != lock["name"]:
            lockitron_lock.name = lock["name"]
            lockitron_lock.save(update_fields=["name"])

        if activity["kind"] != "lock-updated-unlocked":
            return HttpResponse(status=403)

        user, created = LockitronUser.objects.update_or_create(
            user_id=user["id"],
            defaults={
                "email": email,
                "first_name": user.get("first_name"),
                "last_name": user.get("last_name"),
            },
        )

        if (
            created
            and OrganizationDomain.objects.filter(
                domain=email.split("@", 1)[1], organization=lockitron_lock.organization
            ).exists()
        ):
            send_mail(
                "🎉 Welcome to STRUT™!",
                get_template("welcome.txt").render(
                    {
                        "organization": lockitron_lock.organization,
                        "url": request.build_absolute_uri("/"),
                    }
                ),
                settings.DEFAULT_FROM_EMAIL,
                [email],
            )

        try:
            user = User.objects.get(
                email=email,
                organizationmember__organization_id=lockitron_lock.organization_id,
                organizationmember__is_active=True,
            )
        except User.DoesNotExist:
            return HttpResponse(status=404)

        try:
            song = Song.objects.select_related("file").pick_for_user(user)
        except Song.DoesNotExist:
            return HttpResponse()

        for device in Device.objects.filter(
            deviceassociation__organization_id=lockitron_lock.organization_id
        ).iterator():
            device.play_file(song.file)

        return HttpResponse(status=201)
