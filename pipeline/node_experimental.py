import random
from collections import OrderedDict
from collections.abc import Callable, Iterable
from typing import Tuple

class Node():

    @property
    def is_ready(self):
        return all(self._ready.values())

    def __init__(self, fn, name=None, incoming_labels=None, outgoing_labels=None):

        self.fn = fn
        self.name = name
        self.incoming_labels = None
        self.outgoing_labels = None

        # store all incoming and outgoing labels as ordered dictionaries to maintain their mapping to functon's arguments and returns
        if isinstance(incoming_labels, list):
            self.incoming_labels = OrderedDict({key: None for key in incoming_labels})

        if isinstance(outgoing_labels, list):
            self.outgoing_labels = OrderedDict({key: None for key in outgoing_labels})

        # internal mapping for if all upstream data dependacies have been fulfilled
        self._ready = {}

    def store_result(self, label, result):
        if self.incoming_labels is not None:
            if label in self.incoming_labels:
                self.incoming_labels[label] = result

    def run(self):
        results = None
        if self.incoming_labels is not None:
            args = list(self.incoming_labels.values())
            results = self.fn(*args)
        else:
            results = self.fn()
        return results

class Pipeline():
    def __init__(self):
        self.functions = {}
        self.connections = {}
        self.arguments = {}
        self.ready = {}
        self.roots = {}

    def add(self, fn: Callable, incoming_labels=None, outgoing_labels=None):
        self.roots[fn] = fn
        self.functions[fn] = {
            'incoming_labels': incoming_labels if isinstance(incoming_labels, Iterable) else [],
            'outgoing_labels': outgoing_labels if isinstance(outgoing_labels, Iterable) else []
        }
        self.arguments[fn] = OrderedDict({key: None for key in self.functions[fn]['incoming_labels']})
        self.ready[fn] = OrderedDict({key: False for key in self.functions[fn]['incoming_labels']})

    def connect(self, parent: Tuple[Callable, str], child: Tuple[Callable, str]):
        child_fn, child_label = child
        self.connections[parent] = child
        self.ready[child_fn][child_label] = False
        if child_fn in self.roots:
            self.roots.pop(child_fn)

    def start(self):
        for root in self.roots:
            self.run(root)

    def run(self, fn, arguments=None):

        if arguments is not None:
            results = fn(*arguments)
        else:
            results = fn()

        # if only a single value was returned we spoof it as a list
        if len(self.functions[fn]['outgoing_labels']) == 1:
            results = [results]

        for i, outgoing_label in enumerate(self.functions[fn]['outgoing_labels']):
            result = results[i]
            child_fn, child_label = self.connections[(fn, outgoing_label)]

            self.arguments[child_fn][child_label] = result
            self.ready[child_fn][child_label] = True

            if all(self.ready[child_fn].values()):
                print(child_fn, 'ready')
                args = list(self.arguments[child_fn].values())
                self.run(child_fn, arguments=args)
            else:
                print(child_fn, 'waiting')

def hello_world():
    return 'hello world'

def speak(text):
    print(text)

def manipulate(text, deliminator='_'):
    return text.replace(' ', deliminator)

def space():
    return '$'

if __name__ == "__main__":
    pipeline = Pipeline()
    pipeline.add(
            hello_world,
            outgoing_labels=['text'])

    pipeline.add(
            speak,
            incoming_labels=['text'])

    pipeline.add(
            manipulate,
            incoming_labels=['text', 'deliminator'],
            outgoing_labels=['text'])

    pipeline.add(
            space,
            outgoing_labels=['text'])

    pipeline.connect(
            (hello_world, 'text'),
            (manipulate, 'text'))
    
    pipeline.connect(
            (manipulate, 'text'),
            (speak, 'text'))

    pipeline.connect(
            (space, 'text'),
            (manipulate, 'deliminator'))

    pipeline.start()