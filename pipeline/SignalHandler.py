from blinker import signal

class SignalHandler():
    def __init__(self):
        self.start = signal('start')
        self.end = signal('end')
        self.nodeStart = signal('node start')
        self.nodeComplete = signal('node complete')
    