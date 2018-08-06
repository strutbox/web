from django.shortcuts import redirect
from social_core.exceptions import SocialAuthBaseException


class SocialAuthExceptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        if isinstance(exception, SocialAuthBaseException):
            return redirect("/?error=forbidden")
