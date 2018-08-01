import jsonschema
import rapidjson as json
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from structlog import get_logger

from strut.models import LockitronLock, LockitronUser

logger = get_logger()


@method_decorator(csrf_exempt, name="dispatch")
class HooksView(View):
    pass


USER_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "email": {"type": "string"},
        "first_name": {"type": "string"},
        "last_name": {"type": "string"},
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

        data, timestamp = payload["data"], payload["timestamp"]
        lock, user, activity = data["lock"], data["user"], data["activity"]

        lock = LockitronLock.objects.update_or_create(
            lock_id=lock["id"], defaults={"name": lock["name"]}
        )[0]

        user = LockitronUser.objects.update_or_create(
            user_id=user["id"],
            defaults={
                "email": user["email"],
                "first_name": user.get("first_name"),
                "last_name": user.get("last_name"),
            },
        )[0]

        if activity["kind"] != "lock-updated-unlocked":
            return HttpResponse(status=403)

        # print(activity['kind'], lock['id'], user['email'], user['id'])

        return HttpResponse(status=201)
