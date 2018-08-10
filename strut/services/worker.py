import string
from secrets import choice

alphabet = string.ascii_letters + string.digits


def get_name(len=8):
    return "".join(choice(alphabet) for i in range(len))


def sentry_handler():
    from raven.contrib.django.raven_compat.models import client

    def send_to_sentry(job, *exc_info):
        client.captureException(
            exc_info=exc_info,
            extra={
                "job_id": job.id,
                "func": job.func_name,
                "args": job.args,
                "kwargs": job.kwargs,
                "description": job.description,
            },
        )

    return send_to_sentry


class Service:
    def start(self):
        import strut

        strut.setup()

        from rq import Connection, Queue, Worker

        queues = ["default"]
        with Connection():
            Worker(
                map(Queue, queues),
                exception_handlers=[sentry_handler()],
                default_result_ttl=0,
                name=get_name(),
            ).work()
