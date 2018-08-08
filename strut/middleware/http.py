class ProxyFix:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # In theory, this is unsafe since it's blindly trusting XFF,
        # but in reality, this value is being set explicitly
        # by our frontend proxies.
        try:
            request.META["REMOTE_ADDR"] = request.META["HTTP_X_FORWARDED_FOR"].split(
                ",", 1
            )[0]
        except KeyError:
            pass
        return self.get_response(request)
