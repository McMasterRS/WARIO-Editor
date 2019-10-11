import random
import collections

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
            self.incoming_labels = collections.OrderedDict({key: None for key in incoming_labels})

        if isinstance(outgoing_labels, list):
            self.outgoing_labels = collections.OrderedDict({key: None for key in outgoing_labels})

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

    fns = {}
    connections = {}
    results = {}
    ready = {}
    roots = {}

    nodes = {}

    @classmethod
    def add(cls, fn, incoming_labels=None, outgoing_labels=None):

        cls.fns[fn] = {}
        cls.roots[fn] = fn

        cls.nodes[fn] = {}

        # store any incoming labels as an ordered dictionary
        if incoming_labels is not None and isinstance(incoming_labels, list):
            cls.fns[fn]['incoming_labels'] = incoming_labels
            cls.ready[fn] = {}
            cls.nodes[fn] = collections.OrderedDict({key: None for key in incoming_labels})

        # store any outgoing labels as an ordered dictionary
        if outgoing_labels is not None and isinstance(outgoing_labels, list):
            cls.fns[fn]['outgoing_labels'] = outgoing_labels

    @classmethod
    def connect(cls, parent, child):
        child_fn, child_label = child
        cls.connections[parent] = child
        cls.ready[child_fn][child_label] = False
        if child_fn in cls.roots:
            cls.roots.pop(child_fn)

    @classmethod
    def start(cls):
        for root in cls.roots:
            cls.run(root)

    @classmethod
    def run(cls, fn, arguments=None):

        if arguments is not None:
            results = fn(*arguments)
        else:
            results = fn()

        if not isinstance(results, tuple) or not isinstance(results, list):
            results = [results]

        if 'outgoing_labels' in cls.fns[fn]:
            for i, result in enumerate(results):
                result_label = cls.fns[fn]['outgoing_labels'][i]
                child_fn, child_label = cls.connections[(fn, result_label)]

                cls.nodes[child_fn][child_label] = result
                cls.ready[child_fn][child_label] = True

                if all(cls.ready[child_fn].values()):
                    print(child_fn, 'ready')
                    args = list(cls.nodes[child_fn].values())
                    cls.run(child_fn, arguments=args)
                else:
                    print(child_fn, 'waiting')

def hello_world():
    return 'hello world'

Node(hello_world, name='Hello World', outgoing_labels=['text'])

def speak(text):
    print(text)

Node(speak, name='Speak', outgoing_labels=['text'])

def manipulate(text, deliminator='_'):
    return text.replace(' ', deliminator)

Node(manipulate, name='Manipulate', incoming_labels=['text', 'deliminator'], outgoing_labels=['text'])

def space():
    return '$'

if __name__ == "__main__":
    Pipeline.add(
            hello_world,
            outgoing_labels=['text'])

    Pipeline.add(
            speak,
            incoming_labels=['text'])

    Pipeline.add(
            manipulate,
            incoming_labels=['text', 'deliminator'],
            outgoing_labels=['text'])

    Pipeline.add(
            space,
            outgoing_labels=['text'])

    Pipeline.connect(
            (hello_world, 'text'),
            (manipulate, 'text'))
    
    Pipeline.connect(
            (manipulate, 'text'),
            (speak, 'text'))

    Pipeline.connect(
            (space, 'text'),
            (manipulate, 'deliminator'))

    Pipeline.start()