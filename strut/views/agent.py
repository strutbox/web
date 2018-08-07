import re
from secrets import compare_digest
from time import time

import petname
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from django.conf import settings
from django.core.signing import TimestampSigner
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from structlog import get_logger

from dataclasses import dataclass
from strut.http import DeviceResponse
from strut.models import Device, DeviceActivity, FirmwareVersion

logger = get_logger()


class InvalidUserAgent(ValueError):
    pass


@dataclass
class UserAgent:
    version: str
    serial: str

    @classmethod
    def parse(cls, user_agent):
        # User-Agent: Strut/0.0.1-1234567123 (0000000000)
        try:
            return cls(
                *re.match(r"^Strut/([0-9.-]+) \(([a-z0-9]{16})\)$", user_agent).groups()
            )
        except AttributeError:
            raise InvalidUserAgent()


@method_decorator(csrf_exempt, name="dispatch")
class AgentView(View):
    def dispatch(self, request):
        try:
            self.user_agent = UserAgent.parse(request.META["HTTP_USER_AGENT"])
        except KeyError:
            return JsonResponse({"error": "Missing User-Agent header"}, status=400)
        except InvalidUserAgent:
            return JsonResponse({"error": "Malformed User-Agent"}, status=400)

        self.log = logger.new(
            path_info=request.META["PATH_INFO"], ip_address=request.META["REMOTE_ADDR"]
        ).bind(serial=self.user_agent.serial)

        return super().dispatch(request)


class Ping(AgentView):
    def get(self, request):
        try:
            device = Device.objects.get(serial=self.user_agent.serial)
        except Device.DoesNotExist:
            return JsonResponse({"error": "Unknown serial"}, status=404)

        return DeviceResponse(device, {"time": int(time() * 1000)})


class Bootstrap(AgentView):
    def post(self, request):
        try:
            key = serialization.load_pem_public_key(
                request.body, backend=default_backend()
            ).public_bytes(
                encoding=serialization.Encoding.DER,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
        except Exception as e:
            self.log.error(e)
            return JsonResponse({"error": str(e)}, status=500)

        device, created = Device.objects.get_or_create(
            serial=self.user_agent.serial,
            defaults={"pubkey": key, "name": petname.Generate},
        )

        device.log(request, type=DeviceActivity.Type.API_BOOTSTRAP)

        if not created and not compare_digest(key, device.pubkey):
            return JsonResponse({"error": "Public key mismatch!"}, status=400)

        return DeviceResponse(
            device,
            {
                "created": created,
                "device": {"name": device.name, "settings": device.settings or {}},
                "websocket": f"{settings.WEBSOCKET_HOST}/{TimestampSigner().sign(device.serial)}",
                "download_url": f"https://{settings.GOOGLE_STORAGE_BUCKET}.storage.googleapis.com/files/",
            },
        )


class Firmware(AgentView):
    def get(self, request):
        if "application/json" not in request.META.get("HTTP_ACCEPT"):
            return HttpResponse(status=400)
        channel = int(request.META.get("channel", FirmwareVersion.Channel.Device))

        firmware = FirmwareVersion.objects.filter(channel=channel).first()

        if not firmware:
            return HttpResponse(status=404)

        if firmware.version == self.user_agent.version:
            return HttpResponse(status=204)

        return JsonResponse(
            {
                # 'url': '...',
                "url": firmware.version,
                "name": firmware.name,
                "notes": firmware.notes,
                "pub_date": firmware.date_created,
            }
        )
