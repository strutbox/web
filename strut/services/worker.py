class Service:
    def start(self):
        import strut

        strut.setup()

        from time import sleep
        from redis.exceptions import ConnectionError
        from rq import Connection, Queue, Worker

        queues = ["default"]
        config = {"default_result_ttl": 0}
        with Connection():
            Worker(map(Queue, queues), **config).work()
