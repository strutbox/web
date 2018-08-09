def pytest_report_header(config):
    return (
        "*************************************************************************\n"
        "* The best part of waking up is STRUT™, STRUT™, STRUT™, STRUT™, STRUT™. *\n"
        "*************************************************************************"
    )


def pytest_configure(config):
    from django.conf import Settings, settings as django_settings

    settings = Settings("strut.settings")

    for setting, value in dict(
        DEBUG=True,
        SECRET_KEY="STRUT",
        HOST="localhost",
        WEBSOCKET_HOST="ws://localhost:8001",
        ALLOWED_HOSTS=["localhost"],
        SOCIAL_AUTH_GOOGLE_OAUTH2_KEY="",
        SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET="",
        STATIC_URL="/static/",
        GOOGLE_STORAGE_BUCKET="strut-test-bucket",
        DEFAULT_FROM_EMAIL="root@strut",
        RAVEN_CONFIG={},
        CSP_HEADER="script-src 'self'",
    ).items():
        setattr(settings, setting, value)

    django_settings.configure(settings)
