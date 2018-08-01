import structlog
from django.apps import AppConfig


class StrutConfig(AppConfig):
    name = "strut"

    def ready(self):
        setup_logging()
        setup_rq()


def setup_logging():
    from django.conf import settings

    if settings.DEBUG:
        renderer = structlog.processors.KeyValueRenderer(
            key_order=["timestamp", "level", "logger", "event"]
        )
    else:
        from rapidjson import dumps

        renderer = structlog.processors.JSONRenderer(serializer=dumps)
    structlog.configure(
        processors=[
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M.%S"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            renderer,
        ],
        context_class=structlog.threadlocal.wrap_dict(dict),
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def setup_rq():
    from django.conf import settings
    from strut.tasks import manager

    manager.setup(settings)
