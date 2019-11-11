import random
from collections import OrderedDict
from collections.abc import Callable, Collection
from typing import Tuple
from uuid import uuid1

# pipelines are stateful, they remember where data goes, where data is coming from, and everythin about running it
# functions are not, functions are simply functions that have arguments and return values as normal


class Node():
    def __init__(self, fn, title=None:str, incoming_values=None:Collection, outgoing_labels=None:Collection, view_widget=None):
        self.fn = fn
        self.title = title
        self.incoming_values = incoming_values
        self.outgoing_values = outgoing_values
        

class Node():

    def __init__(self, fn: Callable, name=None, incoming_labels=None, outgoing_labels=None):
        'node initialization'
        self.fn = fn
        self.name = name

        self.incoming_labels = incoming_labels
        self.outgoing_labels = outgoing_labels

        # Create empty dictionaries for each of the incoming and outgoing labels if they exist
        incoming_values = {key: True for key in incoming_labels} if isinstance(incoming_labels, Collection) else {}
        outgoing_values = {key: True for key in outgoing_labels} if isinstance(outgoing_labels, Collection) else {}

        # store all incoming and outgoing labels as ordered dictionaries to maintain their mapping to functon's arguments and returns
        self.incoming_values = OrderedDict(incoming_values)
        self.outgoing_values = OrderedDict(outgoing_values)

    def run(self):
        'run this node'
        args = list(self.incoming_values.values())
        results = self.fn(*args) if not args else self.fn()
        for i, result in enumerate(results):
            self.outgoing_values[i] = result
        return results

# each pipeline is an observer of each pipeline_event

class Observable():
    pass

class Observer():
    pass

# Singleton observer of all pipelines
class Pipelines():
    instance = None
    def __init__(self):
        if instance is not None:
            instance = self
        else:
            self = instance

class PipelineObservable():
    pass

class PipelineEvent():

    def __init__(self, event_name):
        self.event_name = event_name

    def emit(self, message):
        pass

on_finish_this = PipelineEvent('on_finish_this')
on_finish_this.emit('done!')

# not a singleton but definitly need some sort of watcher, so lets say a node throws an event we want that event to effect all of the pipelines it is associated
# all pipelines register themselves with the pipeline observer
class Pipeline():
    def __init__(self):
        self.functions = {}
        self.connections = {}
        self.arguments = {}
        self.ready = {}
        self.roots = {}
        self.io = {}

    def add(self, fn: Callable, name:str, incoming_labels=None, outgoing_labels=None):
        self.functions[name] = fn
        self.io[name] = {
            'incoming_labels': incoming_labels if isinstance(incoming_labels, Collection) else [],
            'outgoing_labels': outgoing_labels if isinstance(outgoing_labels, Collection) else []
        }
        self.arguments[name] = OrderedDict({key: None for key in self.io[name]['incoming_labels']})
        self.ready[name] = OrderedDict({key: False for key in self.io[name]['incoming_labels']})
        if incoming_labels is None:
            self.roots[name] = name
        return name

    def connect(self, parent: Tuple[Callable, str], child: Tuple[Callable, str]):
        child_fn, child_label = child
        self.connections[parent] = child
        self.ready[child_fn][child_label] = False
        if child_fn in self.roots:
            self.roots.pop(child_fn)

    def start(self):
        for root in self.roots:
            self.run(root)

    def run(self, fn_name: str, arguments=None):
        fn = self.functions[fn_name]

        results = fn(*arguments) if arguments is not None else fn()

        for i, outgoing_label in enumerate(self.io[fn_name]['outgoing_labels']):
            result = results[i] if len(self.io[fn_name]['outgoing_labels']) > 1 else results
            if (fn_name, outgoing_label) in self.connections:
                child_fn, child_label = self.connections[(fn_name, outgoing_label)]

                self.arguments[child_fn][child_label] = result
                self.ready[child_fn][child_label] = True

                if all(self.ready[child_fn].values()):
                    self.run(child_fn, arguments=list(self.arguments[child_fn].values()))

class Terminal():
    def __init__(self, label, connected_to=None):
        self.label = label
        self.connected_to = connected_to

class Node():
    def __init__(self, fn, incoming_labels=None, outgoing_labels=None):
        self.fn = fn
        self.incoming_labels = incoming_labels
        self.outgoing_labels = outgoing_labels
        self.incoming_terminals = OrderedDict({label: Terminal(label) for label in incoming_labels})
        self.outgoing_terminals = OrderedDict({label: None for Terminal(label) in outgoing_labels})

    def run(self):
        pass

    def delete(self):
        pass

##############################################################################################

def increment(value, amount=1):
    return value + amount

    # nd_increment = Node(increment, title_label="" incoming_labels=[], outgoing_labels=[])
    # nd_random_value = Node(input_random, title_label="" incoming_labels=[], outgoing_labels=[])
    # nd_random_amount = Node(input_random, title_label="" incoming_labels=[], outgoing_labels=[])
    # connect(parent=[(nd_random_value, 'value'), (nd_random_amount, 'value')], child=nd_increment)
    # nd_random_amount.connect(nd_increment.terminals['values])

def decrement(value, amount=1):
    return value - amount

def input_random():
    return random.random()

def print_value(value):
    print(value)

# nodes are simply functions with labels
if __name__ == "__main__":
    pipeline = Pipeline()

    pipeline.add(
        increment,
        title_label='Increment',
        incoming_labels=['value', 'amount'],
        outgoing_labels=['value'],
    )

    pipeline.add(
        decrement, 'Decrement',
        incoming_labels=['value', 'amount'],
        outgoing_labels=['value']
    )

    nd_random_value = pipeline.add(
        input_random, 'Random Value',
        outgoing_labels=['value']
    )

    pipeline.add(
        input_random, 'Random Amount',
        outgoing_labels=['value']
    )

    nd_print_value = pipeline.add(
        print_value, 'Print Value',
        outgoing_labels=['value']
    )

    pipeline.connect((nd_random_value, 'value'), (nd_print_value, 'value'))

    pipeline.start()
