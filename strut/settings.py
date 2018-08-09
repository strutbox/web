import os

import dj_database_url
from click import types

try:
    from uwsgi import opt as uwsgi_options
except ImportError:
    uwsgi_options = {}

_type = type


def env(key, default="", type=None):
    "Extract an environment variable for use in configuration"

    key = "STRUT_" + key

    # First check an internal cache, so we can `pop` multiple times
    # without actually losing the value.
    try:
        rv = env._cache[key]
    except KeyError:
        # We don't want/can't pop off env variables when
        # uwsgi is in autoreload mode, otherwise it'll have an empty
        # env on reload
        if uwsgi_options.get("py-autoreload") == b"1":
            fn = os.environ.__getitem__
        else:
            fn = os.environ.pop

        try:
            rv = fn(key)
            env._cache[key] = rv
        except KeyError:
            rv = default

    if type is None:
        type = types.convert_type(_type(default))

    return type(rv)


env._cache = {}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


SECRET_KEY = env("SECRET_KEY")

DEBUG = env("DEBUG", default=False)

HOST = env("HOST", default="localhost")
WEBSOCKET_HOST = env("WEBSOCKET_HOST", default="ws://localhost:8001")

if DEBUG:
    ALLOWED_HOSTS = ["*"]
else:
    ALLOWED_HOSTS = [HOST]

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "social_django",
    "raven.contrib.django.raven_compat",
    "strut.apps.StrutConfig",
]

MIDDLEWARE = [
    "strut.middleware.http.ProxyFix",
    "strut.middleware.security.CSPMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "strut.social_auth.middleware.SocialAuthExceptionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "strut.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.template.context_processors.static",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
            "builtins": [
                "django.contrib.staticfiles.templatetags.staticfiles",
                "strut.templatetags.core",
            ],
        },
    }
]

WSGI_APPLICATION = "strut.wsgi.application"
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

DATABASES = {
    "default": dj_database_url.config(
        "STRUT_DATABASE_URL", default="postgres://strut@127.0.0.1:5432/strut"
    )
}

AUTH_USER_MODEL = "strut.User"

AUTHENTICATION_BACKENDS = [
    "social_core.backends.google.GoogleOAuth2",
    # 'django.contrib.auth.backends.ModelBackend',
]

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = env("GOOGLE_OAUTH2_CLIENT_ID")
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = env("GOOGLE_OAUTH2_CLIENT_SECRET")
SOCIAL_AUTH_GOOGLE_OAUTH2_USER_FIELDS = ["email"]
SOCIAL_AUTH_PIPELINE = (
    "social_core.pipeline.social_auth.social_details",
    "social_core.pipeline.social_auth.social_uid",
    "social_core.pipeline.social_auth.social_user",
    "strut.social_auth.pipeline.auth_allowed",
    "social_core.pipeline.user.create_user",
    "social_core.pipeline.social_auth.associate_user",
    "social_core.pipeline.social_auth.load_extra_data",
    "social_core.pipeline.user.user_details",
    "social_core.pipeline.social_auth.associate_by_email",
)
SOCIAL_AUTH_URL_NAMESPACE = "social"
SOCIAL_AUTH_LOGIN_REDIRECT_URL = "index"

SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = env("STATIC_URL", "/static/")

SILENCED_SYSTEM_CHECKS = ["auth.W004"]

DISALLOWED_ORGANIZATION_SLUGS = frozenset(("api", "static"))


GOOGLE_STORAGE_BUCKET = env("GOOGLE_STORAGE_BUCKET")

ASGI_APPLICATION = "strut.routing.application"
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": [("127.0.0.1", 6379)]},
    }
}


EMAIL_BACKEND = env(
    "EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend"
)
EMAIL_HOST = env("EMAIL_HOST")
EMAIL_PORT = env("EMAIL_PORT", default=25)
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = env("EMAIL_USE_TLS", default=False)
EMAIL_USE_SSL = env("EMAIL_USE_SSL", default=False)
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="noreply@localhost")

RAVEN_CONFIG = {
    "dsn": os.environ.get("SENTRY_DSN"),
    "release": os.environ.get("BUILD_REVISION"),
    "environment": "debug" if DEBUG else "production",
    "include_paths": ["strut"],
}

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_SECONDS = 31536000

CSP_HEADER = f"script-src 'self'; style-src 'self'; img-src 'self' https://img.youtube.com; media-src https://{GOOGLE_STORAGE_BUCKET}.storage.googleapis.com; font-src 'self'; connect-src 'self'"
