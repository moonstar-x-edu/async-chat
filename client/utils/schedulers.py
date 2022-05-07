from threading import Thread
from time import sleep


class IntervalExecutor(Thread):
    def __init__(self, interval: int, fn):
        Thread.__init__(self)
        self.daemon = True

        self.interval = interval
        self.fn = fn

        self.should_execute = True

    def stop(self):
        self.should_execute = False

    def run(self):
        while self.should_execute:
            sleep(self.interval)
            self.fn()
