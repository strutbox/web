class QueueManager:
    def setup(self, settings):
        from redis import StrictRedis

        r = StrictRedis()
        self.queues = {}

        from rq import Queue

        for q in ["default"]:
            self.queues[q] = Queue(q, connection=r)

    def get(self, queue):
        return self.queues[queue]


manager = QueueManager()


def enqueue(func, queue=None, *args, **kwargs):
    q = manager.get(queue or "default")
    return q.enqueue(func, *args, **kwargs)
