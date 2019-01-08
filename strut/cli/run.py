from dataclasses import dataclass
from typing import Tuple

import click


@dataclass
class AddressType:
    ipv4: Tuple[str, int]
    fd: int
    unix: str


class AddressParamType(click.ParamType):
    name = "address"

    def __call__(self, value, param=None, ctx=None):
        if value is None:
            return (None, None)
        return self.convert(value, param, ctx)

    def convert(self, value, param, ctx):
        d = {"ipv4": None, "fd": None, "unix": None}

        try:
            if value[:3] == "fd@":
                d["fd"] = int(value[3:])
            elif value[:1] == "/":
                d["unix"] = value
            else:
                if ":" in value:
                    host, port = value.split(":", 1)
                    port = int(port)
                else:
                    host = value
                    port = None
                d["ipv4"] = host, port
        except ValueError:
            self.fail(f'"{value}" is not a valid address')

        return AddressType(**d)


Address = AddressParamType()


@click.group()
def run():
    "Run stuff."


@run.command()
@click.option("--dev", default=False, is_flag=True)
@click.option("--bind", default="0.0.0.0:8000", type=Address)
@click.option("--workers", default=1)
def web(dev, bind, workers):
    "Start the webserver."
    from strut.services.http import Service

    Service(dev, bind, workers).start()


def _run_worker():
    from strut.services.worker import Service

    Service().start()


@run.command()
@click.option("-n", default=1)
def worker(n):
    if n == 1:
        _run_worker()
    else:
        from multiprocessing import Process

        procs = []
        for _ in range(n):
            p = Process(target=_run_worker)
            p.start()
            procs.append(p)

        for p in procs:
            try:
                p.join()
            except KeyboardInterrupt:
                pass


@run.command()
@click.option("--bind", default="0.0.0.0:8001", type=Address)
def push(bind):
    from strut.services.push import Service

    Service(bind).start()
