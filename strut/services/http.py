import os

dev_options = {"py_autoreload": 1, "worker_reload_mercy": 1, "honour_stdin": True}


class Service:
    def __init__(self, dev, bind, workers):
        self.dev = dev
        self.workers = workers
        self.bind = bind

    def start(self):
        if self.bind.ipv4:
            bind = f"{self.bind.ipv4[0]}:{self.bind.ipv4[1]}"
        elif self.bind.unix:
            bind = self.bind.unix
        else:
            raise ValueError("Cannot bind to fd")

        options = {"offload_threads": "%k", "processes": self.workers, "threads": 4}

        if self.dev:
            options.update(dev_options)
            os.environ["STRUT_DEBUG"] = "true"

        import mywsgi

        mywsgi.run("strut.wsgi:application", bind, **options)
