from threading import Thread


class EventEmitter(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True

        self.handlers = dict()

    def on(self, event: str, fn):
        handlers = self.handlers.get(event)

        if handlers is None:
            self.handlers[event] = []

        self.handlers[event].append(fn)

    def off(self, event: str):
        self.handlers[event] = None

    def emit(self, event: str, args: list):
        if args is None:
            args = []

        handlers = self.handlers.get(event)

        if handlers:
            for fn in handlers:
                fn(*args)
