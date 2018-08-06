import os
import sys

dev_options = {
    "py-autoreload": 1,
    "protocol": "http",
    "worker-reload-mercy": 1,
    "honour-stdin": True,
}


class Service:
    def __init__(self, dev, bind, workers):
        self.dev = dev
        self.workers = workers
        self.bind = bind

    def start(self):
        options = {
            "auto-procname": True,
            "die-on-term": True,
            "disable-write-exception": True,
            "enable-threads": True,
            "ignore-sigpipe": True,
            "ignore-write-errors": True,
            "lazy-apps": True,
            "master": True,
            "module": "strut.wsgi:application",
            "need-app": True,
            "offload-threads": "%k",
            "processes": self.workers,
            "protocol": "http",
            "single-interpreter": True,
            "threads": 4,
            "thunder-lock": True,
            "virtualenv": sys.prefix,
            "vacuum": True,
            "log-format": '%(addr) - %(user) [%(ltime)] "%(method) %(uri) %(proto)" %(status) %(size) "%(referer)" "%(uagent)"',
        }

        if self.bind.ipv4:
            options["http-socket"] = f"{self.bind.ipv4[0]}:{self.bind.ipv4[1]}"
        elif self.bind.unix:
            options["socket"] = self.bind.unix
            options["chmod-socket"] = 777
        else:
            raise ValueError("Cannot bind to fd")

        if self.dev:
            options.update(dev_options)
            os.environ["STRUT_DEBUG"] = "true"

        for k, v in options.items():
            if v is None:
                continue
            key = "UWSGI_" + k.upper().replace("-", "_")
            if isinstance(v, str):
                value = v
            elif v is True:
                value = "true"
            elif v is False:
                value = "false"
            elif isinstance(v, int):
                value = str(v)
            else:
                raise TypeError("Unknown option type: %r (%s)" % (k, type(v)))

            os.environ[key] = value

        os.execvp("uwsgi", ("uwsgi",))
