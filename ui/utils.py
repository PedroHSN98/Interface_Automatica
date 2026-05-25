import queue


class QueueOutput:
    def __init__(self, q: queue.Queue, tag: str = "normal"):
        self.q = q
        self.tag = tag

    def write(self, text: str):
        if text:
            self.q.put((self.tag, text))

    def flush(self):
        pass
