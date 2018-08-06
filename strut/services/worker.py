import string
from secrets import choice

alphabet = string.ascii_letters + string.digits


def get_name(len=8):
    return "".join(choice(alphabet) for i in range(len))


class Service:
    def start(self):
        import strut

        strut.setup()

        from rq import Connection, Queue, Worker

        queues = ["default"]
        with Connection():
            Worker(map(Queue, queues), default_result_ttl=0, name=get_name()).work()
